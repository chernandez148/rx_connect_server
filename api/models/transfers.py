from datetime import datetime
from config import db

class Transfer(db.Model):
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    from_pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)  # Pharmacy transferring prescription
    to_pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)  # Pharmacy receiving prescription
    transfer_status = db.Column(db.String(50), default='pending')
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prescription = db.relationship('Prescription', back_populates='transfers')
    from_pharmacy = db.relationship('Pharmacy', foreign_keys=[from_pharmacy_id])
    to_pharmacy = db.relationship('Pharmacy', foreign_keys=[to_pharmacy_id])
    
    def __repr__(self):
        return f"<Transfer prescription {self.prescription_id} from {self.from_pharmacy.name} to {self.to_pharmacy.name}>"

