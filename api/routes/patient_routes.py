# server/api/routes/patient_routes.py

from flask import Blueprint
from controllers.patient_controller import CreatePatient, GetPatientsByPharmacyID
from flask_restful import Api

patient_bp = Blueprint('patient_bp', __name__)
api = Api(patient_bp)

# Register Resource
api.add_resource(CreatePatient, "/create_patient")
api.add_resource(GetPatientsByPharmacyID, "/<int:pharmacy_id>/patients")  # <-- Fixed this line
