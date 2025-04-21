# server/api/routes/prescription_routes.py

from flask import Blueprint
from controllers.transfer_controller import CreateTransfer, GetTransfersByPharmacyID, UpdateTransfer
from flask_restful import Api

transfer_bp = Blueprint('transfer_bp', __name__)
api = Api(transfer_bp)

# Register Resource
api.add_resource(CreateTransfer, "/create_transfer")
api.add_resource(GetTransfersByPharmacyID, "/<int:pharmacy_id>/transfers")  # <-- Fixed this line
api.add_resource(UpdateTransfer, '/transfers/<int:transfer_id>')
