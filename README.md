# Microservicio Blacklist

API REST en Flask que gestiona una lista negra global de correos. En local usa PostgreSQL vía **Docker Compose**; el despliegue previsto es **AWS Elastic Beanstalk**.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose v2
- Python **3.8–3.11** (recomendado por las versiones fijadas en `requirements.txt`)

## Paso a paso: levantar el servicio

### 1. Variables de entorno

En la raíz del repositorio:

```bash
cp .env.example .env
```

Edita `.env` si cambias usuario, contraseña o base de datos. **Importante:** `DATABASE_URL` debe coincidir con `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y con el puerto publicado por Docker (por defecto `5432`).

Docker Compose lee `POSTGRES_*` desde ese `.env` al arrancar el contenedor.

### 2. Base de datos con Docker Compose

```bash
docker compose up -d
```

Comprueba que el servicio esté en marcha (y opcionalmente *healthy*):

```bash
docker compose ps
docker compose logs -f db
```

### 3. Entorno Python e instalación de dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

La aplicación carga automáticamente el archivo `.env` gracias a `python-dotenv` en `config.py`.

### 4. Arrancar la API

Con el virtualenv activado y desde la raíz del proyecto:

```bash
python application.py
```

Por defecto el servidor escucha en **http://127.0.0.1:5000**. En el primer arranque se crean las tablas necesarias (`db.create_all()`).

---

## Pruebas manuales

Todas las rutas protegidas exigen el header:

`Authorization: Bearer <STATIC_TOKEN>`

(el valor de `STATIC_TOKEN` en tu `.env`, por defecto `my-static-bearer-token`).

### Con `curl`

**POST — agregar email (201):**

```bash
curl -s -w "\nHTTP: %{http_code}\n" -X POST http://127.0.0.1:5000/blacklists \
  -H "Authorization: Bearer my-static-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "blocked_reason": "Spam reiterado"
  }'
```

`blocked_reason` es opcional.

**GET — consultar si un email está listado (200):**

```bash
curl -s -H "Authorization: Bearer my-static-bearer-token" \
  "http://127.0.0.1:5000/blacklists/usuario@ejemplo.com"
```

**Sin token (401):**

```bash
curl -s -X POST http://127.0.0.1:5000/blacklists \
  -H "Content-Type: application/json" \
  -d '{"email":"otro@ejemplo.com","app_uuid":"550e8400-e29b-41d4-a716-446655440000"}'
```

**Email inválido (400):** repite el POST con `"email": "no-es-email"`.

**Duplicado (409):** ejecuta dos veces el mismo POST con el mismo `email`.

### Con Postman o cliente HTTP similar

| Paso | Método | URL | Headers | Body |
|------|--------|-----|---------|------|
| Alta | POST | `http://127.0.0.1:5000/blacklists` | `Authorization: Bearer …`, `Content-Type: application/json` | JSON con `email`, `app_uuid` y opcionalmente `blocked_reason` |
| Consulta | GET | `http://127.0.0.1:5000/blacklists/{email}` | `Authorization: Bearer …` | — |

Sustituye `{email}` por el correo (por ejemplo `usuario@ejemplo.com`).

---

## Comandos útiles de Docker

| Acción | Comando |
|--------|---------|
| Parar contenedores | `docker compose stop` |
| Parar y eliminar contenedores (conserva el volumen de datos) | `docker compose down` |
| Eliminar también los datos de PostgreSQL | `docker compose down -v` |

---

## Problemas frecuentes

- **Puerto 5432 ocupado:** cambia en `docker-compose.yml` el mapeo a `"5433:5432"` y actualiza el puerto en `DATABASE_URL` dentro de `.env`.
- **Error de conexión a la base:** asegúrate de que `docker compose up -d` haya terminado y que `DATABASE_URL` apunte a `localhost` con el puerto correcto.
- **401 en todas las peticiones:** el token en `Authorization: Bearer` debe ser exactamente el valor de `STATIC_TOKEN` en `.env`.

---
