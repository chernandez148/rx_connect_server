from marshmallow import Schema, fields
from api.schemas.pharmacy_schema import PharmacySchema

class UserSchema(Schema):
    id = fields.Int()
    pharmacy_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    username = fields.Str()
    email = fields.Str()
    role = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    pharmacy = fields.Nested(PharmacySchema)  # Nested pharmacy schema
    