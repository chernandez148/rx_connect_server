from config import db
from datetime import datetime

class Pharmacy(db.Model):
    __tablename__ = 'pharmacies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    license_number = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship(
        'User', 
        back_populates='pharmacy_rel',
        lazy=True
    )
    pharmacy_prescriptions = db.relationship(
        'PharmacyPrescription',
        back_populates='pharmacy',
        cascade='all, delete-orphan'
    )
    prescriptions = db.relationship(
        'Prescription',
        secondary='pharmacy_prescriptions',
        back_populates='pharmacies',
        overlaps="pharmacy_prescriptions,pharmacy"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'address': self.address,
            'license_number': self.license_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Pharmacy {self.name}>"
