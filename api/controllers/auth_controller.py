from flask import request, jsonify
from werkzeug.security import check_password_hash
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt
)
from datetime import timedelta
from models.users import User
from models.pharmacies import Pharmacy  # Ensure Pharmacy model is imported
from utils.blacklist import token_blacklist
from marshmallow import Schema, fields
from schemas.pharmacy_schema import PharmacySchema
from schemas.user_schema import UserSchema  # Assuming UserSchema is defined in schemas/user_schema.py

class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return {"msg": "Missing email or password"}, 400

        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return {"msg": "Bad email or password"}, 401

        pharmacy = Pharmacy.query.filter_by(id=user.pharmacy_id).first()

        # Use Marshmallow to serialize the user and pharmacy
        user_schema = UserSchema()
        pharmacy_schema = PharmacySchema()

        user_data = user_schema.dump(user)
        pharmacy_data = pharmacy_schema.dump(pharmacy) if pharmacy else None

        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1)
        )

        print(pharmacy_data)  # Debugging step to confirm serialization

        return {
            "access_token": access_token,
            "user": user_data,
            "pharmacy": pharmacy_data  # Include pharmacy details
        }, 200


class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        token_blacklist.add(jti)
        return {"msg": "Successfully logged out"}, 200
