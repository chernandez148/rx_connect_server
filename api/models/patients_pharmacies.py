from datetime import datetime
from config import db

class PatientsPharmacy(db.Model):
    __tablename__ = 'patients_pharmacies'

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    def __repr__(self):
        return f"<PatientsPharmacy(patient_id={self.patient_id}, pharmacy_id={self.pharmacy_id})>"
