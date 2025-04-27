# server/api/routes/prescription_routes.py

from flask import Blueprint
from controllers.prescription_controller import CreatePrescription, GetPrescriptionByPharmacyID, GetPrescriptionByID, UpdatePrescription
from flask_restful import Api

prescription_bp = Blueprint('prescription_bp', __name__)
api = Api(prescription_bp)

# Register Resource
api.add_resource(CreatePrescription, "/create_prescription")
api.add_resource(GetPrescriptionByPharmacyID, "/<int:pharmacy_id>/prescriptions") 
api.add_resource(GetPrescriptionByID, '/prescriptions/<int:prescription_id>')
api.add_resource(UpdatePrescription, '/prescriptions/<int:prescription_id>')
