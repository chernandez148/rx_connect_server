# server/api/controllers/pharmacy_controller.py

from flask import request, current_app, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.pharmacies import Pharmacy 
from config import db

class CreatePharmacy(Resource):
    def post(self):
        data = request.get_json()

        # Required fields
        required_fields = ['name', 'phone_number', 'address', 'license_number']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        try:
            new_pharmacy = Pharmacy(
                name=data['name'],
                phone_number=data['phone_number'],
                address=data['address'],
                license_number=data['license_number']
            )

            db.session.add(new_pharmacy)
            db.session.commit()

            return make_response({
                'message': 'New pharmacy added successfully',
                'pharmacy': new_pharmacy.to_dict()
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({'error': 'Pharmacy with this license number already exists.'}, 409)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class GetPharmacies(Resource):
    def get(self):
        # Read pagination params from query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Calculate offset and limit
        offset = (page - 1) * per_page

        # Query with limit and offset
        total_count = Pharmacy.query.count()
        pharmacies = Pharmacy.query.offset(offset).limit(per_page).all()

        return make_response({
            "pharmacies": [pharmacy.to_dict() for pharmacy in pharmacies],
            "pagination": {
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page,
                "current_page": page,
                "per_page": per_page
            }
        }, 200)

