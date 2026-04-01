import os


class Config:
    # Base de datos – en producción se sobreescribe con variable de entorno
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/blacklist_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT – token estático (permitido por el enunciado)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-static-key")

    # Token estático para autenticación de sistemas internos
    STATIC_TOKEN = os.environ.get("STATIC_TOKEN", "my-static-bearer-token")
