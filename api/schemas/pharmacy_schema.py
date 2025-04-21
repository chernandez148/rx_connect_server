from marshmallow import Schema, fields

class PharmacySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    phone_number = fields.Str()
    address = fields.Str()
    license_number = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()