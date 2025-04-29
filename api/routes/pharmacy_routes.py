# server/api/routes/pharmacy_routes.py

from flask import Blueprint
from api.controllers.pharmacy_controller import CreatePharmacy, GetPharmacies
from flask_restful import Api

pharmacy_bp = Blueprint('pharmacy_bp', __name__)
api = Api(pharmacy_bp)

# Register Resource
api.add_resource(CreatePharmacy, "/create_pharmacy")
api.add_resource(GetPharmacies, "/pharmacies")
