#server/api/models/users.py
from datetime import datetime
from config import db
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM
from .serializer import SerializerMixin

class UserRole(Enum):
    ADMIN = 'admin'
    PHARMACIST = 'pharmacist'
    TECHNICIAN = 'technician'

role_enum = ENUM(UserRole, name="user_role", create_type=True)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(role_enum, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pharmacy = db.relationship("Pharmacy", back_populates="users")

    SERIALIZE_EXCLUDE = ['password']
    SERIALIZE_INCLUDE = ['pharmacy']

    def __repr__(self):
        return f"<User {self.username}>"
