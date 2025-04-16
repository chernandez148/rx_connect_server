from config import db
from datetime import datetime

class PharmacyPrescription(db.Model):
    __tablename__ = 'pharmacy_prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)

    pharmacy = db.relationship(
        'Pharmacy',
        back_populates='pharmacy_prescriptions',
        overlaps="prescriptions,pharmacies"
    )
    prescription = db.relationship(
        'Prescription',
        back_populates='pharmacy_prescriptions',
        overlaps="prescriptions,pharmacies"
    )
