from marshmallow import fields, validate

from models.blacklist_entry import BlacklistEntry
from schemas import ma


class BlacklistEntrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BlacklistEntry
        load_instance = True

    email = fields.Email(required=True)
    app_uuid = fields.String(required=True)
    blocked_reason = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
    )
