from flask import request, current_app, make_response, g
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from config import db
import re

from models import Patient, Pharmacy, User, Prescription, PharmacyPatients ,PharmacyPrescription

class CreatePatient(Resource):
    def post(self):
        data = request.get_json()

        # Required fields check
        required_fields = ['first_name', 'last_name', 'dob', 'sex', 'pharmacy_ids']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        # Validate pharmacy_ids is a list
        if not isinstance(data['pharmacy_ids'], list):
            return make_response({'error': 'pharmacy_ids must be a list'}, 400)

        # Email validation
        if data.get('email'):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                return make_response({'error': 'Invalid email format.'}, 400)
            email = data['email'].lower()
        else:
            email = None

        # Date validation
        try:
            dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
        except ValueError:
            return make_response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 400)

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

            db.session.add(new_patient)
            db.session.flush()  # Get the ID without committing

            # Associate the patient with pharmacies
            pharmacy_ids = data['pharmacy_ids']
            if not pharmacy_ids:  # At least one pharmacy required
                return make_response({'error': 'At least one pharmacy ID is required'}, 400)

            # Verify all pharmacies exist in a single query
            existing_pharmacies = {p.id for p in Pharmacy.query.filter(
                Pharmacy.id.in_(pharmacy_ids)
            ).all()}
            
            missing_pharmacies = set(pharmacy_ids) - existing_pharmacies
            if missing_pharmacies:
                return make_response({
                    'error': 'One or more pharmacies not found',
                    'missing_ids': list(missing_pharmacies)
                }, 404)

            # Create associations
            associations = [
                PharmacyPatients(patient_id=new_patient.id, pharmacy_id=pid)
                for pid in pharmacy_ids
            ]
            db.session.bulk_save_objects(associations)
            
            db.session.commit()

            return make_response({
                'message': 'New patient added successfully',
                'patient': new_patient.to_dict()
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {str(e)}")
            if 'email' in str(e).lower():
                return make_response({'error': 'Patient with this email address already exists.'}, 409)
            if 'phone_number' in str(e).lower():
                return make_response({'error': 'Patient with this phone number already exists.'}, 409)
            return make_response({'error': 'Database integrity error'}, 400)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
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

class GetPatientByID(Resource):
    @jwt_required()  # Protect this route with JWT authentication
    def get(self, patient_id):
        try:
            patient = Patient.query.get(patient_id)

            if not patient:
                return make_response({'error': 'Patient not found.'}, 404)

            patient_dict = patient.to_dict(exclude=['pharmacies'])

            current_user_id = get_jwt_identity()

            # Check if the current user is associated with a pharmacy
            pharmacy_id = db.session.query(User.pharmacy_id).filter(User.id == current_user_id).scalar()

            if pharmacy_id:
                prescriptions = (
                    db.session.query(Prescription)
                    .join(PharmacyPrescription)
                    .filter(
                        Prescription.patient_id == patient_id,
                        PharmacyPrescription.pharmacy_id == pharmacy_id
                    )
                    .all()
                )
                patient_dict['prescriptions'] = [p.to_dict() for p in prescriptions]
            else:
                patient_dict['prescriptions'] = []

            return make_response({'patient': patient_dict}, 200)

        except Exception as e:
            current_app.logger.error(f"Error retrieving patient by ID: {e}", exc_info=True)
            return make_response({'error': 'Internal server error'}, 500)


class PatchPatientByID(Resource):
    @jwt_required()
    def patch(self, patient_id):
        data = request.get_json()

        patient = Patient.query.get(patient_id)
        if not patient:
            return make_response({'error': 'Patient not found'}, 404)

        try:
            if "email" in data:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                    return make_response({'error': 'Invalid email format.'}, 400)
                patient.email = data["email"].lower()

            if "dob" in data:
                try:
                    patient.dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
                except ValueError:
                    return make_response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 400)

            # Update basic fields
            for field in ['first_name', 'last_name', 'sex', 'phone_number', 'address']:
                if field in data:
                    setattr(patient, field, data[field])

            # Update pharmacy associations if provided
            if "pharmacy_ids" in data:
                if not isinstance(data["pharmacy_ids"], list):
                    return make_response({'error': 'pharmacy_ids must be a list'}, 400)

                # Validate pharmacy IDs
                existing_pharmacies = {p.id for p in Pharmacy.query.filter(
                    Pharmacy.id.in_(data["pharmacy_ids"])
                ).all()}

                missing = set(data["pharmacy_ids"]) - existing_pharmacies
                if missing:
                    return make_response({
                        'error': 'One or more pharmacy IDs not found',
                        'missing_ids': list(missing)
                    }, 404)

                # Remove old associations
                PharmacyPatients.query.filter_by(patient_id=patient.id).delete()

                # Create new associations
                new_links = [
                    PharmacyPatients(patient_id=patient.id, pharmacy_id=pid)
                    for pid in data["pharmacy_ids"]
                ]
                db.session.bulk_save_objects(new_links)

            db.session.commit()
            return make_response({'message': 'Patient updated successfully', 'patient': patient.to_dict()}, 200)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError during PATCH: {str(e)}")
            if 'email' in str(e).lower():
                return make_response({'error': 'Patient with this email address already exists.'}, 409)
            return make_response({'error': 'Database integrity error'}, 400)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error in PATCH: {str(e)}", exc_info=True)
            return make_response({'error': 'Internal server error'}, 500)