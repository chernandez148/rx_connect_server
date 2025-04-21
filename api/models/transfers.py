from datetime import datetime
from config import db
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM  # If using PostgreSQL

class TransferStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

status_enum = ENUM(TransferStatus, name="transfer_status", create_type=True)

class Transfer(db.Model):
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)

    # Optional after approval
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=True)

    # Required
    from_pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    to_pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False) 

    # Patient Info
    patient_first_name = db.Column(db.String(100), nullable=False)
    patient_last_name = db.Column(db.String(100), nullable=False)
    patient_dob = db.Column(db.Date, nullable=False)
    patient_phone_number = db.Column(db.String(200), nullable=True)  

    # Prescription Info (external input, not from your Prescription model)
    medication_name = db.Column(db.String(200), nullable=False)

    transfer_status = db.Column(status_enum, nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prescription = db.relationship('Prescription', back_populates='transfers', foreign_keys=[prescription_id])
    from_pharmacy = db.relationship('Pharmacy', foreign_keys=[from_pharmacy_id])
    to_pharmacy = db.relationship('Pharmacy', foreign_keys=[to_pharmacy_id])

    def to_dict(self):
        return {
            "id": self.id,
            "prescription_id": self.prescription_id,
            "from_pharmacy_id": self.from_pharmacy_id,
            "to_pharmacy_id": self.to_pharmacy_id,
            "patient_first_name": self.patient_first_name,
            "patient_last_name": self.patient_last_name,
            "patient_dob": self.patient_dob.isoformat(),
            "patient_phone_number": self.patient_phone_number,
            "medication_name": self.medication_name,
            "transfer_status": self.transfer_status.value,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "completed_by": self.completed_by,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Transfer request for {self.medication_name} from pharmacy {self.from_pharmacy_id} to {self.to_pharmacy_id}>"
