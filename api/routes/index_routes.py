# server/api/routes/index_routes.py

from flask import Blueprint
from api.controllers.index_controller import Index
from flask_restful import Api

index_bp = Blueprint('index_bp', __name__)
api = Api(index_bp)

# Register Resource
api.add_resource(Index, "/")
