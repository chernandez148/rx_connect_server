#server/api/models/phamracies.py
from config import db
from datetime import datetime
from .serializer import SerializerMixin

class Pharmacy(db.Model, SerializerMixin):
    __tablename__ = 'pharmacies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    license_number = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', back_populates='pharmacy')
    pharmacy_prescriptions = db.relationship('PharmacyPrescription', back_populates='pharmacy')
    prescriptions = db.relationship('Prescription', secondary='pharmacy_prescriptions', back_populates='pharmacies')
    pharmacy_patients = db.relationship('PharmacyPatients', back_populates='pharmacy')
    patients = db.relationship('Patient', secondary='pharmacy_patients', back_populates='pharmacies')

    SERIALIZE_EXCLUDE = ['users', 'prescriptions', 'pharmacy_prescriptions', 'pharmacy_patients']
    SERIALIZE_INCLUDE = []  # No need to include anything extra

    def __repr__(self):
        return f"<Pharmacy {self.name}>"