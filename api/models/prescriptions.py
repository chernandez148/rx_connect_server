# server/api/models/prescriptions.py
from config import db
from datetime import datetime
from .serializer import SerializerMixin

class Prescription(db.Model, SerializerMixin):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    directions_for_use = db.Column(db.Text, nullable=True)  # New
    quantity = db.Column(db.Integer, nullable=False)
    refills = db.Column(db.Integer, nullable=True)  # New
    date_of_prescription = db.Column(db.Date, nullable=True)  # New
    date_last_filled = db.Column(db.Date, nullable=True)  # New
    prescriber_full_name = db.Column(db.String(200), nullable=True)  # New
    prescriber_dea_number = db.Column(db.String(50), nullable=True)  # New
    prescriber_contact_info = db.Column(db.String(200), nullable=True)  # New

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', back_populates='prescriptions')
    transfers = db.relationship('Transfer', back_populates='prescription')
    pharmacy_prescriptions = db.relationship(
        'PharmacyPrescription',
        back_populates='prescription',
        cascade='all, delete-orphan'
    )
    pharmacies = db.relationship(
        'Pharmacy',
        secondary='pharmacy_prescriptions',
        back_populates='prescriptions',
        viewonly=True
    )

    SERIALIZE_EXCLUDE = ['patient_id']
    SERIALIZE_INCLUDE = ['patient', 'pharmacies', 'transfers']

    def __repr__(self):
        return f"<Prescription {self.medication}>"
