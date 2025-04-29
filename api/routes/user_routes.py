# server/api/routes/user_routes.py

from flask import Blueprint
from api.controllers.user_controller import CreateUser, GetUsersByPharmacyID
from flask_restful import Api

user_bp = Blueprint('user_bp', __name__)
api = Api(user_bp)

# Register Resource
api.add_resource(CreateUser, "/create_user")
api.add_resource(GetUsersByPharmacyID, "/<int:pharmacy_id>/users")  # <-- Fixed this line
