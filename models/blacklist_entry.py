import uuid
from datetime import datetime

from models import db


class BlacklistEntry(db.Model):
    __tablename__ = "blacklisted_emails"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    request_ip = db.Column(db.String(45), nullable=False)  # IPv4 o IPv6
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
