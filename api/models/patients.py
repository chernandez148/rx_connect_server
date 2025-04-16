from datetime import datetime
from config import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prescriptions = db.relationship('Prescription', back_populates='patient')  # ✅ Added this line

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dob': self.dob,
            'sex': self.sex,
            'phone_number': self.phone_number,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"
