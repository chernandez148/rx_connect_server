#server/api/models/pharmacy_prescriptions.py
from config import db
from .serializer import SerializerMixin

class PharmacyPrescription(db.Model, SerializerMixin):
    __tablename__ = 'pharmacy_prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)

    pharmacy = db.relationship('Pharmacy', back_populates='pharmacy_prescriptions')
    prescription = db.relationship('Prescription', back_populates='pharmacy_prescriptions')

    SERIALIZE_EXCLUDE = ['pharmacy_id', 'prescription_id']
    SERIALIZE_INCLUDE = ['pharmacy', 'prescription']

    def __repr__(self):
        return f"<PharmacyPrescription {self.pharmacy_id}-{self.prescription_id}>"