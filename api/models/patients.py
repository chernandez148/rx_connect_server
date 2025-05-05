#server/api/models/patients.py
from datetime import datetime
from api.config import db
from .serializer import SerializerMixin
from sqlalchemy import event
from utils.encryption import encrypt_field, decrypt_field

class Patient(db.Model, SerializerMixin):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    _dob = db.Column('dob', db.LargeBinary, nullable=False)  # Encrypted storage
    _sex = db.Column('sex', db.LargeBinary, nullable=False)  # Encrypted storage
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    prescriptions = db.relationship('Prescription', back_populates='patient')
    pharmacy_patients = db.relationship(
        'PharmacyPatients',
        back_populates='patient',
        cascade='all, delete-orphan'
    )
    pharmacies = db.relationship(
        'Pharmacy',
        secondary='pharmacy_patients',
        back_populates='patients',
        viewonly=True
    )

    SERIALIZE_EXCLUDE = ['pharmacies', '_dob', '_sex']
    SERIALIZE_INCLUDE = ['prescriptions', 'dob', 'sex']

    @property
    def dob(self):
        return decrypt_field(self._dob) if self._dob else None

    @dob.setter
    def dob(self, value):
        self._dob = encrypt_field(value)

    @property
    def sex(self):
        return decrypt_field(self._sex) if self._sex else None

    @sex.setter
    def sex(self, value):
        self._sex = encrypt_field(value)

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"

@event.listens_for(Patient, 'before_insert')
@event.listens_for(Patient, 'before_update')
def sanitize_patient_data(mapper, connection, target):
    """Sanitize all string fields to prevent XSS"""
    target.first_name = bleach.clean(target.first_name, strip=True)
    target.last_name = bleach.clean(target.last_name, strip=True)
    if target.address:
        target.address = bleach.clean(target.address, strip=True)