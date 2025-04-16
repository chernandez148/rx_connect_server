from datetime import datetime
from config import db
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM  # Only if using PostgreSQL

class UserRole(Enum):
    ADMIN = 'admin'
    OWNER = 'owner'
    PHARMACY_MANAGER = 'pharmacy_manager'
    OPERATIONS_MANAGER = 'operations_manager'
    HR_MANAGER = 'hr_manager'
    PHARMACIST_IN_CHARGE = 'pharmacist_in_charge'
    PHARMACIST = 'pharmacist'
    STAFF_PHARMACIST = 'staff_pharmacist'
    INTERN_PHARMACIST = 'intern_pharmacist'
    PHARMACY_TECHNICIAN = 'pharmacy_technician'

role_enum = ENUM(UserRole, name="user_role", create_type=True)

class User(db.Model):
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

    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'role': self.role.value if self.role else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<User {self.username}>"
