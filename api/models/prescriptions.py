from config import db
from datetime import datetime

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('Patient', back_populates='prescriptions')

    pharmacy_prescriptions = db.relationship(
        'PharmacyPrescription',
        back_populates='prescription',
        cascade='all, delete-orphan'
    )
    pharmacies = db.relationship(
        'Pharmacy',
        secondary='pharmacy_prescriptions',
        back_populates='prescriptions',
        overlaps="pharmacy_prescriptions,prescription"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "medication": self.medication,
            "dosage": self.dosage,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Prescription {self.medication} for patient {self.patient_id}>"
