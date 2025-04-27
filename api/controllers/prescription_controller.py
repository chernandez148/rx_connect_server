from flask import request, current_app, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models.prescriptions import Prescription  # Make sure this exists
from models.pharmacy_prescriptions import PharmacyPrescription
from models.pharmacies import Pharmacy
from config import db

class CreatePrescription(Resource):
    def post(self):
        data = request.get_json()

        # Required fields check
        required_fields = ['patient_id', 'medication', 'dosage', 'quantity', 'pharmacy_ids']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        try:
            # Create new Prescription object
            new_prescription = Prescription(
                patient_id=data['patient_id'],
                medication=data['medication'],
                dosage=data['dosage'],
                quantity=data['quantity'],
                directions_for_use=data.get('directions_for_use', None),  # Optional, will be None if not provided
                refills=data.get('refills', None),  # Optional, will be None if not provided
                date_of_prescription=data.get('date_of_prescription', None),  # Optional, will be None if not provided
                date_last_filled=data.get('date_last_filled', None),  # Optional, will be None if not provided
                prescriber_full_name=data.get('prescriber_full_name', None),  # Optional, will be None if not provided
                prescriber_dea_number=data.get('prescriber_dea_number', None),  # Optional, will be None if not provided
                prescriber_contact_info=data.get('prescriber_contact_info', None),  # Optional, will be None if not provided
            )

            db.session.add(new_prescription)
            db.session.commit()

            # Associate the prescription with pharmacies
            pharmacy_ids = data['pharmacy_ids']
            pharmacies = Pharmacy.query.filter(Pharmacy.id.in_(pharmacy_ids)).all()

            if len(pharmacies) != len(pharmacy_ids):
                return make_response({'error': 'One or more pharmacies not found.'}, 404)

            for pharmacy in pharmacies:
                association = PharmacyPrescription(
                    prescription_id=new_prescription.id,
                    pharmacy_id=pharmacy.id
                )
                db.session.add(association)

            db.session.commit()

            return make_response({
                'message': 'New prescription created successfully.',
                'prescription': new_prescription.to_dict()  # Make sure you have a to_dict() method
            }, 201)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({'error': 'Integrity constraint failed.'}, 409)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class GetPrescriptionByPharmacyID(Resource):
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
            prescriptions_query = Prescription.query.join(Prescription.pharmacies).filter(Pharmacy.id == pharmacy_id)
            total_count = prescriptions_query.count()
            prescriptions = prescriptions_query.offset(offset).limit(per_page).all()

            return make_response({
                "prescriptions": [prescription.to_dict() for prescription in prescriptions],
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

class GetPrescriptionByID(Resource):
    def get(self, prescription_id):
        try:
            prescription = Prescription.query.get(prescription_id)
            if not prescription:
                return make_response({'error': 'Prescription not found.'}, 404)

            return make_response({'prescription': prescription.to_dict()}, 200)

        except Exception as e:
            current_app.logger.error(f"Error fetching prescription by ID: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class UpdatePrescription(Resource):
    def patch(self, prescription_id):
        data = request.get_json()

        try:
            prescription = Prescription.query.get(prescription_id)
            if not prescription:
                return make_response({'error': 'Prescription not found.'}, 404)

            # Optional fields to update
            if 'patient_id' in data:
                prescription.patient_id = data['patient_id']
            if 'medication' in data:
                prescription.medication = data['medication']
            if 'dosage' in data:
                prescription.dosage = data['dosage']
            if 'quantity' in data:
                prescription.quantity = data['quantity']
            if 'refills' in data:
                prescription.refills = data['refills']
            if 'directions_for_use' in data:
                prescription.directions_for_use = data['directions_for_use']
            if 'date_of_prescription' in data:
                # Ensure the date format is correct before saving
                prescription.date_of_prescription = datetime.strptime(data['date_of_prescription'], '%Y-%m-%d').date() if data['date_of_prescription'] else None
            if 'date_last_filled' in data:
                # Ensure the date format is correct before saving
                prescription.date_last_filled = datetime.strptime(data['date_last_filled'], '%Y-%m-%d').date() if data['date_last_filled'] else None
            if 'prescriber_full_name' in data:
                prescription.prescriber_full_name = data['prescriber_full_name']
            if 'prescriber_dea_number' in data:
                prescription.prescriber_dea_number = data['prescriber_dea_number']
            if 'prescriber_contact_info' in data:
                prescription.prescriber_contact_info = data['prescriber_contact_info']

            if 'pharmacy_ids' in data:
                # Clear existing associations with pharmacies
                PharmacyPrescription.query.filter_by(prescription_id=prescription.id).delete()

                # Validate and create new associations with pharmacies
                pharmacy_ids = data['pharmacy_ids']
                pharmacies = Pharmacy.query.filter(Pharmacy.id.in_(pharmacy_ids)).all()

                if len(pharmacies) != len(pharmacy_ids):
                    return make_response({'error': 'One or more pharmacies not found.'}, 404)

                for pharmacy in pharmacies:
                    association = PharmacyPrescription(
                        prescription_id=prescription.id,
                        pharmacy_id=pharmacy.id
                    )
                    db.session.add(association)

            db.session.commit()

            return make_response({
                'message': 'Prescription updated successfully.',
                'prescription': prescription.to_dict()
            }, 200)

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"IntegrityError: {e}")
            return make_response({'error': 'Integrity constraint failed.'}, 409)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)
