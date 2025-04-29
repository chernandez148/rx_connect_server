#server/api/models/messages.py

from datetime import datetime
from api.config import db
from .serializer import SerializerMixin

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfers.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    SERIALIZE_EXCLUDE = ['transfer_id', 'sender_id', 'receiver_id']
    SERIALIZE_INCLUDE = ['transfer', 'sender', 'receiver']

    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.receiver_id}>"