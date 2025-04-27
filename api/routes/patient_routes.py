# server/api/routes/patient_routes.py

from flask import Blueprint
from controllers.patient_controller import CreatePatient, PatchPatientByID,GetPatientsByPharmacyID, GetPatientByID
from flask_restful import Api

patient_bp = Blueprint('patient_bp', __name__)
api = Api(patient_bp)

# Register Resource
api.add_resource(CreatePatient, "/create_patient")
api.add_resource(PatchPatientByID, '/patient/<int:patient_id>')
api.add_resource(GetPatientsByPharmacyID, "/<int:pharmacy_id>/patients")
api.add_resource(GetPatientByID, '/patient/<int:patient_id>')

