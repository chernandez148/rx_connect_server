# server/api/controllers/user_controller.py

from flask import request, current_app, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from api.models.users import User
from werkzeug.security import generate_password_hash
from api.config import db
import re

class CreateUser(Resource):
    def post(self):
        data = request.get_json()

        required_fields = ['pharmacy_id', 'first_name', 'last_name', 'username', 'email', 'role', 'password']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return make_response({'error': 'Invalid email format.'}, 400)

        email = data['email'].lower()
        username = data['username'].lower()
        hashed_password = generate_password_hash(data['password'])

        try:
            new_user = User(
                pharmacy_id=data['pharmacy_id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                username=username,
                email=email,
                role=data['role'],
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            return make_response({
                'message': 'New user added successfully',
                'user': new_user.to_dict()
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({'error': 'User with this email address already exists.'}, 409)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class GetUsersByPharmacyID(Resource):
    def get(self, pharmacy_id):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        offset = (page - 1) * per_page

        users_query = User.query.filter_by(pharmacy_id=pharmacy_id)
        total_count = users_query.count()
        users = users_query.offset(offset).limit(per_page).all()

        return make_response({
            "users": [user.to_dict() for user in users],
            "pagination": {
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page,
                "current_page": page,
                "per_page": per_page
            }
        }, 200)

class GetUserByID(Resource):
    def get(self, user_id):
        try:
            user = User.query.get(user_id)
            
            if not user:
                return make_response({'error': 'User not found'}, 404)
                
            return make_response({
                'user': user.to_dict()
            }, 200)
            
        except Exception as e:
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class PatchUserByID(Resource):
    def patch(self, user_id):
        data = request.get_json()
        
        if not data:
            return make_response({'error': 'No data provided for update'}, 400)
            
        try:
            user = User.query.get(user_id)
            
            if not user:
                return make_response({'error': 'User not found'}, 404)
            
            # List of allowed fields that can be updated
            allowed_fields = {
                'first_name', 'last_name', 'username', 'email', 'role', 'password'
            }
            
            # Check for any invalid fields in the request
            invalid_fields = set(data.keys()) - allowed_fields
            if invalid_fields:
                return make_response({
                    'error': f'Invalid fields for update: {", ".join(invalid_fields)}'
                }, 400)
            
            # Update email if provided
            if 'email' in data:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                    return make_response({'error': 'Invalid email format.'}, 400)
                user.email = data['email'].lower()
            
            # Update username if provided
            if 'username' in data:
                user.username = data['username'].lower()
            
            # Update password if provided (hash it first)
            if 'password' in data:
                user.password = generate_password_hash(data['password'])
            
            # Update other fields
            for field in ['first_name', 'last_name', 'role']:
                if field in data:
                    setattr(user, field, data[field])
            
            db.session.commit()
            
            return make_response({
                'message': 'User updated successfully',
                'user': user.to_dict()
            }, 200)
            
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({
                'error': 'Database integrity error (possibly duplicate email or username)'
            }, 409)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)
