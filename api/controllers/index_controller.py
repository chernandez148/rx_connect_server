#server/api/controllers/index_controller.py

from flask import jsonify
from flask_restful import Resource

class Index(Resource):
    def get(self):
        return jsonify({'message': 'Welcome to the API'})
