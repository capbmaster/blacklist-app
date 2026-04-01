from functools import wraps

from flask import current_app, request
from flask_restful import Resource

from models import db
from models.blacklist_entry import BlacklistEntry
from schemas.blacklist_schema import BlacklistEntrySchema


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"msg": "Token de autorización requerido"}, 401
        token = auth_header.split(" ", 1)[1].strip()
        if not token or token != current_app.config["STATIC_TOKEN"]:
            return {"msg": "Token inválido"}, 401
        return f(*args, **kwargs)

    return decorated


class BlacklistResource(Resource):
    @token_required
    def post(self):
        """
        Agrega un email a la lista negra global.
        Body JSON:
          - email       (string, requerido, formato email válido)
          - app_uuid    (string, requerido, UUID)
          - blocked_reason (string, opcional, máx 255 chars)

        El microservicio captura automáticamente:
          - request_ip: IP de origen del request
          - created_at: fecha/hora UTC actual

        Respuestas:
          201: {"msg": "El email fue agregado a la lista negra"}
          400: {"msg": "Datos de entrada inválidos", "errors": {...}}
          409: {"msg": "El email ya existe en la lista negra"}
          401: Token inválido o ausente
        """
        schema = BlacklistEntrySchema()
        data = request.get_json()

        errors = schema.validate(data)
        if errors:
            return {"msg": "Datos de entrada inválidos", "errors": errors}, 400

        existing = BlacklistEntry.query.filter_by(email=data["email"]).first()
        if existing:
            return {"msg": "El email ya existe en la lista negra"}, 409

        entry = BlacklistEntry(
            email=data["email"],
            app_uuid=data["app_uuid"],
            blocked_reason=data.get("blocked_reason"),
            request_ip=request.remote_addr,
        )
        db.session.add(entry)
        db.session.commit()

        return {"msg": "El email fue agregado a la lista negra"}, 201


class BlacklistQueryResource(Resource):
    @token_required
    def get(self, email):
        """
        Consulta si un email está en la lista negra global.
        Parámetro URL: email

        Respuestas:
          200: {"blacklisted": true,  "blocked_reason": "motivo"}
          200: {"blacklisted": false, "blocked_reason": null}
          401: Token inválido o ausente
        """
        entry = BlacklistEntry.query.filter_by(email=email).first()

        if entry:
            return {
                "blacklisted": True,
                "blocked_reason": entry.blocked_reason,
            }, 200

        return {
            "blacklisted": False,
            "blocked_reason": None,
        }, 200
