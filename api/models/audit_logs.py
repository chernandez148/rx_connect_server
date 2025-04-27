#server/api/models/audit_logs.py
from datetime import datetime
from config import db
from .serializer import SerializerMixin

class AuditLog(db.Model, SerializerMixin):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    SERIALIZE_EXCLUDE = []
    SERIALIZE_INCLUDE = []

    def __repr__(self):
        return f"<AuditLog {self.action_type}>"