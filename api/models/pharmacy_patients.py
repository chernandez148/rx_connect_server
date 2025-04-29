#server/api/models/pharmacy_patients.py
from api.config import db
from .serializer import SerializerMixin

class PharmacyPatients(db.Model, SerializerMixin):
    __tablename__ = 'pharmacy_patients'

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    pharmacy = db.relationship('Pharmacy', back_populates='pharmacy_patients')
    patient = db.relationship('Patient', back_populates='pharmacy_patients')

    SERIALIZE_EXCLUDE = ['pharmacy_id', 'patient_id']
    SERIALIZE_INCLUDE = ['pharmacy', 'patient']

    def __repr__(self):
        return f"<PharmacyPatient {self.pharmacy_id}-{self.patient_id}>"

