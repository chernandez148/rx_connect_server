# server/api/routes/auth_routes.py

from flask import Blueprint
from controllers.auth_controller import Login, Logout
from flask_restful import Api

auth_bp = Blueprint('auth_bp', __name__)
api = Api(auth_bp)

# Register Resource
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")  # <-- Fixed this line
