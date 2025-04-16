from flask import request, current_app, make_response
from flask_restful import Resource
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from models.patients import Patient
from models.patients_pharmacies import PatientsPharmacy
from models.pharmacies import Pharmacy
from config import db
import re

class CreatePatient(Resource):
    def post(self):
        data = request.get_json()

        # Required fields check
        required_fields = ['pharmacy_ids', 'first_name', 'last_name', 'dob', 'sex']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        # Email validation
        if data.get('email') and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return make_response({'error': 'Invalid email format.'}, 400)

        email = data['email'].lower() if data.get('email') else None
        dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()

        try:
            # Create new Patient object
            new_patient = Patient(
                first_name=data['first_name'],
                last_name=data['last_name'],
                dob=dob,
                sex=data['sex'],
                phone_number=data.get('phone_number'),
                email=email,
                address=data.get('address')
            )

            # Add the new patient to the session
            db.session.add(new_patient)
            db.session.commit()

            # Now, associate the patient with multiple pharmacies
            pharmacy_ids = data['pharmacy_ids']  # List of pharmacy IDs
            pharmacies = Pharmacy.query.filter(Pharmacy.id.in_(pharmacy_ids)).all()

            if len(pharmacies) != len(pharmacy_ids):  # If some pharmacy IDs are not found
                return make_response({'error': 'One or more pharmacies not found.'}, 404)

            # Create association in the PatientsPharmacy table for each pharmacy
            for pharmacy in pharmacies:
                patient_pharmacy_association = PatientsPharmacy(
                    patient_id=new_patient.id,
                    pharmacy_id=pharmacy.id
                )
                db.session.add(patient_pharmacy_association)

            db.session.commit()

            return make_response({
                'message': 'New patient added successfully',
                'patient': new_patient.to_dict()
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({'error': 'User with this email address already exists.'}, 409)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)


class GetPatientsByPharmacyID(Resource):
    def get(self, pharmacy_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            offset = (page - 1) * per_page

            # Check if pharmacy exists
            pharmacy = Pharmacy.query.get(pharmacy_id)
            if not pharmacy:
                return make_response({'error': 'Pharmacy not found.'}, 404)

            # Query patients associated with the pharmacy
            patients_query = Patient.query.join(Patient.pharmacies).filter(Pharmacy.id == pharmacy_id)
            total_count = patients_query.count()
            patients = patients_query.offset(offset).limit(per_page).all()

            return make_response({
                "patients": [patient.to_dict() for patient in patients],
                "pagination": {
                    "total_count": total_count,
                    "total_pages": (total_count + per_page - 1) // per_page,
                    "current_page": page,
                    "per_page": per_page
                }
            }, 200)

        except Exception as e:
            current_app.logger.error(f"Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)
