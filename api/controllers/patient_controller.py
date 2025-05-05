from flask import request, current_app, make_response, g
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from config import db
import re
import bleach
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Patient, Pharmacy, User, Prescription, PharmacyPatients, PharmacyPrescription
from decorators.role_check import requires_permission
from schemas import PatientSchema, PatientUpdateSchema
from utils.audit_log import log_audit_event

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize schemas for validation
patient_schema = PatientSchema()
patient_update_schema = PatientUpdateSchema()

class CreatePatient(Resource):
    decorators = [
        jwt_required(),
        requires_permission('add_patient'),
        limiter.limit("10/minute")
    ]

    def post(self):
        data = request.get_json()
        
        # Validate input
        errors = patient_schema.validate(data)
        if errors:
            return make_response({'error': errors}, 400)
        
        current_user = User.query.get(get_jwt_identity())
        
        # Force pharmacy association for non-admins
        if current_user.role not in ['SuperAdmin', 'PharmacyManager']:
            if not current_user.pharmacy_id:
                return make_response(
                    {'error': 'You must be associated with a pharmacy to add patients'},
                    403
                )
            data['pharmacy_ids'] = [current_user.pharmacy_id]

        try:
            # Create new patient
            new_patient = Patient(
                first_name=data['first_name'],
                last_name=data['last_name'],
                dob=data['dob'],
                sex=data['sex'],
                phone_number=data.get('phone_number'),
                email=data.get('email'),
                address=data.get('address')
            )

            db.session.add(new_patient)
            db.session.flush()

            # Associate with pharmacies
            pharmacy_ids = data['pharmacy_ids']
            existing_pharmacies = {p.id for p in Pharmacy.query.filter(
                Pharmacy.id.in_(pharmacy_ids)
            ).all()}
            
            missing_pharmacies = set(pharmacy_ids) - existing_pharmacies
            if missing_pharmacies:
                return make_response({
                    'error': 'One or more pharmacies not found',
                    'missing_ids': list(missing_pharmacies)
                }, 404)

            associations = [
                PharmacyPatients(patient_id=new_patient.id, pharmacy_id=pid)
                for pid in pharmacy_ids
            ]
            db.session.bulk_save_objects(associations)
            db.session.commit()

            # Log the creation
            log_audit_event(
                user_id=current_user.id,
                action='create_patient',
                entity_type='patient',
                entity_id=new_patient.id,
                details={'pharmacy_ids': pharmacy_ids}
            )

            return make_response({
                'message': 'New patient added successfully',
                'patient': new_patient.to_dict()
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {str(e)}")
            if 'email' in str(e).lower():
                return make_response(
                    {'error': 'Patient with this email already exists'},
                    409
                )
            return make_response({'error': 'Database integrity error'}, 400)

class GetPatientsByPharmacyID(Resource):
    decorators = [
        jwt_required(),
        requires_permission('view_patient'),
        limiter.limit("60/minute")
    ]

    def get(self, pharmacy_id):
        current_user = User.query.get(get_jwt_identity())
        
        # Scope limitation for non-admins
        if current_user.role in ['Pharmacist', 'Technician', 'Clerk']:
            if not current_user.pharmacy_id or str(current_user.pharmacy_id) != str(pharmacy_id):
                return make_response(
                    {'error': 'Access restricted to your pharmacy'},
                    403
                )

        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 10, type=int), 100)

            pharmacy = Pharmacy.query.get(pharmacy_id)
            if not pharmacy:
                return make_response({'error': 'Pharmacy not found'}, 404)

            patients = Patient.query.join(Patient.pharmacies)\
                .filter(Pharmacy.id == pharmacy_id)\
                .paginate(page=page, per_page=per_page, error_out=False)

            return make_response({
                "patients": [p.to_dict() for p in patients.items],
                "pagination": {
                    "total": patients.total,
                    "pages": patients.pages,
                    "current_page": page,
                    "per_page": per_page
                }
            }, 200)

        except Exception as e:
            current_app.logger.error(f"Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class PatchPatientByID(Resource):
    decorators = [
        jwt_required(),
        requires_permission('edit_patient'),
        limiter.limit("20/minute")
    ]

    def patch(self, patient_id):
        current_user = User.query.get(get_jwt_identity())
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return make_response({'error': 'Patient not found'}, 404)

        # Scope limitation for non-admins
        if current_user.role in ['Pharmacist', 'Technician']:
            if not current_user.pharmacy_id:
                return make_response(
                    {'error': 'You must be associated with a pharmacy'},
                    403
                )
            
            if not PharmacyPatients.query.filter_by(
                patient_id=patient_id,
                pharmacy_id=current_user.pharmacy_id
            ).first():
                return make_response(
                    {'error': 'Patient not in your pharmacy'},
                    404
                )

        data = request.get_json()
        errors = patient_update_schema.validate(data)
        if errors:
            return make_response({'error': errors}, 400)

        # Field restrictions for Technicians
        if current_user.role == 'Technician':
            restricted_fields = ['dob', 'sex']
            restricted_updates = set(data.keys()) & set(restricted_fields)
            if restricted_updates:
                return make_response({
                    'error': 'Restricted field modification',
                    'restricted_fields': list(restricted_updates)
                }, 403)

        try:
            original_data = patient.to_dict()
            
            # Update fields
            for field in ['first_name', 'last_name', 'phone_number', 'email', 'address']:
                if field in data:
                    setattr(patient, field, data[field])

            if 'dob' in data and current_user.role != 'Technician':
                patient.dob = data['dob']

            if 'sex' in data and current_user.role != 'Technician':
                patient.sex = data['sex']

            # Handle pharmacy associations
            if "pharmacy_ids" in data and current_user.role in ['SuperAdmin', 'PharmacyManager']:
                existing = {p.id for p in Pharmacy.query.filter(
                    Pharmacy.id.in_(data["pharmacy_ids"])
                ).all()}
                
                missing = set(data["pharmacy_ids"]) - existing
                if missing:
                    return make_response({
                        'error': 'Invalid pharmacy IDs',
                        'missing_ids': list(missing)
                    }, 404)

                PharmacyPatients.query.filter_by(patient_id=patient.id).delete()
                db.session.bulk_save_objects([
                    PharmacyPatients(patient_id=patient.id, pharmacy_id=pid)
                    for pid in data["pharmacy_ids"]
                ])

            db.session.commit()

            # Log the changes
            log_audit_event(
                user_id=current_user.id,
                action='update_patient',
                entity_type='patient',
                entity_id=patient.id,
                details={
                    'original': original_data,
                    'changes': data
                }
            )

            return make_response({
                'message': 'Patient updated',
                'patient': patient.to_dict()
            }, 200)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {str(e)}")
            return make_response({'error': 'Database error'}, 400)