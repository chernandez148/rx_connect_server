from flask import request, jsonify
from werkzeug.security import check_password_hash
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt
)
from datetime import timedelta
from api.models.users import User
from api.models.pharmacies import Pharmacy  # Ensure Pharmacy model is imported
from api.utils.blacklist import token_blacklist
from marshmallow import Schema, fields
from api.schemas.pharmacy_schema import PharmacySchema
from api.schemas.user_schema import UserSchema  # Assuming UserSchema is defined in schemas/user_schema.py

class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return {"msg": "Missing email or password"}, 400

        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return {"msg": "Bad email or password"}, 401

        # Create the serializer instances
        user_schema = UserSchema()
        
        # Serialize the user (which will include pharmacy via the nested schema)
        user_data = user_schema.dump(user)

        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1)
        )

        return {
            "access_token": access_token,
            "user": user_data  # Now includes pharmacy info in the user object
        }, 200

class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        token_blacklist.add(jti)
        return {"msg": "Successfully logged out"}, 200
