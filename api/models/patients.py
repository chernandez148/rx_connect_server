#server/api/models/patients.py
from datetime import datetime
from config import db
from .serializer import SerializerMixin

class Patient(db.Model, SerializerMixin):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    SERIALIZE_EXCLUDE = ['pharmacies']
    SERIALIZE_INCLUDE = ['prescriptions']

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"