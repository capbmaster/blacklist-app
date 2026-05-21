"""
Pruebas de estrés para blacklist-app.
Escenarios diseñados para generar métricas en New Relic:
  - Tiempo de respuesta de servicios (endpoints POST/GET)
  - Tiempo de respuesta de DB (queries pesadas)
  - Apdex (mezcla de requests rápidos y lentos)
  - Errores (requests inválidos, duplicados, sin auth)
  - Alertas (picos de carga)
"""

import random
import string
import uuid

from locust import HttpUser, between, task, tag


def random_email():
    prefix = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domains = ["example.com", "test.org", "demo.net", "stress.io"]
    return f"{prefix}@{random.choice(domains)}"


TOKEN = "super-secret-static-key"  # Cambiar si tu STATIC_TOKEN es diferente
AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}"}


class BlacklistStressUser(HttpUser):
    """Usuario simulado que ejecuta operaciones mixtas contra la API."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Registra algunos emails al inicio para tener datos en GET."""
        self.registered_emails = []
        for _ in range(5):
            email = random_email()
            self.client.post(
                "/blacklists",
                json={
                    "email": email,
                    "app_uuid": str(uuid.uuid4()),
                    "blocked_reason": "seed data",
                },
                headers=AUTH_HEADERS,
            )
            self.registered_emails.append(email)

    # --- ESCENARIOS PARA TIEMPO DE RESPUESTA DE SERVICIOS ---

    @tag("response_time", "post")
    @task(3)
    def post_new_email(self):
        """POST exitoso - mide tiempo de respuesta del servicio + escritura DB."""
        self.client.post(
            "/blacklists",
            json={
                "email": random_email(),
                "app_uuid": str(uuid.uuid4()),
                "blocked_reason": random.choice(["spam", "fraude", "phishing", None]),
            },
            headers=AUTH_HEADERS,
            name="POST /blacklists (nuevo)",
        )

    @tag("response_time", "get")
    @task(5)
    def get_existing_email(self):
        """GET de email existente - mide tiempo de respuesta + lectura DB."""
        email = random.choice(self.registered_emails)
        self.client.get(
            f"/blacklists/{email}",
            headers=AUTH_HEADERS,
            name="GET /blacklists/{email} (existe)",
        )

    @tag("response_time", "get")
    @task(3)
    def get_nonexistent_email(self):
        """GET de email inexistente - mide query DB sin resultado."""
        self.client.get(
            f"/blacklists/{random_email()}",
            headers=AUTH_HEADERS,
            name="GET /blacklists/{email} (no existe)",
        )

    # --- ESCENARIOS PARA APDEX (mezcla satisfactorio/tolerante/frustrado) ---

    @tag("apdex", "health")
    @task(4)
    def health_check(self):
        """Health check rápido - contribuye a Apdex satisfactorio."""
        self.client.get("/health", name="GET /health")

    @tag("apdex", "burst")
    @task(1)
    def burst_posts(self):
        """Ráfaga de 10 POSTs seguidos - genera latencia y afecta Apdex."""
        for _ in range(10):
            self.client.post(
                "/blacklists",
                json={
                    "email": random_email(),
                    "app_uuid": str(uuid.uuid4()),
                    "blocked_reason": "burst test " + "x" * 200,
                },
                headers=AUTH_HEADERS,
                name="POST /blacklists (burst)",
            )

    # --- ESCENARIOS PARA REGISTRO DE ERRORES ---

    @tag("errors")
    @task(2)
    def post_without_auth(self):
        """POST sin token - genera error 401."""
        self.client.post(
            "/blacklists",
            json={"email": random_email(), "app_uuid": str(uuid.uuid4())},
            name="POST /blacklists (sin auth - 401)",
        )

    @tag("errors")
    @task(2)
    def post_invalid_email(self):
        """POST con email inválido - genera error 400."""
        self.client.post(
            "/blacklists",
            json={
                "email": "not-an-email",
                "app_uuid": str(uuid.uuid4()),
            },
            headers=AUTH_HEADERS,
            name="POST /blacklists (email inválido - 400)",
        )

    @tag("errors")
    @task(1)
    def post_missing_fields(self):
        """POST sin campos requeridos - genera error 400."""
        self.client.post(
            "/blacklists",
            json={"blocked_reason": "missing fields"},
            headers=AUTH_HEADERS,
            name="POST /blacklists (campos faltantes - 400)",
        )

    @tag("errors")
    @task(2)
    def post_duplicate_email(self):
        """POST duplicado - genera error 409."""
        email = random.choice(self.registered_emails)
        self.client.post(
            "/blacklists",
            json={"email": email, "app_uuid": str(uuid.uuid4())},
            headers=AUTH_HEADERS,
            name="POST /blacklists (duplicado - 409)",
        )

    @tag("errors")
    @task(1)
    def post_invalid_token(self):
        """POST con token incorrecto - genera error 401."""
        self.client.post(
            "/blacklists",
            json={"email": random_email(), "app_uuid": str(uuid.uuid4())},
            headers={"Authorization": "Bearer token-invalido"},
            name="POST /blacklists (token inválido - 401)",
        )


class HighLoadUser(HttpUser):
    """Usuario de carga alta para disparar alertas en New Relic."""

    wait_time = between(0.1, 0.5)
    weight = 1  # Menos usuarios de este tipo

    @tag("alerts", "spike")
    @task
    def rapid_fire_gets(self):
        """GETs muy rápidos para generar picos de throughput."""
        self.client.get(
            f"/blacklists/{random_email()}",
            headers=AUTH_HEADERS,
            name="GET /blacklists/{email} (high-load)",
        )

    @tag("alerts", "spike")
    @task
    def rapid_fire_posts(self):
        """POSTs rápidos para estresar la DB."""
        self.client.post(
            "/blacklists",
            json={
                "email": random_email(),
                "app_uuid": str(uuid.uuid4()),
                "blocked_reason": "high load test",
            },
            headers=AUTH_HEADERS,
            name="POST /blacklists (high-load)",
        )
