from flask import request, current_app, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest
from datetime import datetime
from api.models.transfers import Transfer, TransferStatus
from api.models.pharmacies import Pharmacy
from api.config import db

class CreateTransfer(Resource):
    def post(self):
        data = request.get_json()

        required_fields = [
            'from_pharmacy_id',
            'to_pharmacy_id',
            'requested_by',
            'patient_first_name',
            'patient_last_name',
            'patient_dob',
            'medication_name',
            'transfer_status'
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return make_response({'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400)

        try:
            # Parse enum safely
            try:
                transfer_status = TransferStatus(data['transfer_status'])
            except ValueError:
                return make_response({'error': f"Invalid transfer_status. Must be one of: {[s.value for s in TransferStatus]}"}, 400)

            new_transfer = Transfer(
                prescription_id=data.get('prescription_id'),
                from_pharmacy_id=data['from_pharmacy_id'],
                to_pharmacy_id=data['to_pharmacy_id'],
                patient_first_name=data['patient_first_name'],
                patient_last_name=data['patient_last_name'],
                patient_dob=datetime.strptime(data['patient_dob'], '%Y-%m-%d'),
                patient_phone_number=data.get('patient_phone_number'),
                medication_name=data['medication_name'],
                transfer_status=transfer_status,
                requested_by=data['requested_by']
            )

            db.session.add(new_transfer)
            db.session.commit()

            return make_response({
                'message': 'New transfer initiated',
                'transfer': new_transfer.to_dict()
            }, 201)

        except IntegrityError as ie:
            db.session.rollback()
            current_app.logger.error(f"Integrity Error: {ie}")
            return make_response({'error': 'Integrity constraint violated'}, 400)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class GetTransfersByPharmacyID(Resource):
    def get(self, pharmacy_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            pharmacy = Pharmacy.query.get(pharmacy_id)
            if not pharmacy:
                return make_response({'error': 'Pharmacy not found.'}, 404)

            transfers_query = Transfer.query.filter(
                (Transfer.to_pharmacy_id == pharmacy_id) | (Transfer.from_pharmacy_id == pharmacy_id)
            )

            total_count = transfers_query.count()
            transfers = transfers_query.offset((page - 1) * per_page).limit(per_page).all()

            return make_response({
                "transfers": [transfer.to_dict() for transfer in transfers],
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

class GetTransferByID(Resource):
    def get(self, transfer_id):
        try:
            transfer = Transfer.query.get(transfer_id)

            if not transfer:
                return make_response({'error': 'Transfer not found'}, 404)

            return make_response({'transfer': transfer.to_dict()}, 200)

        except Exception as e:
            current_app.logger.error(f"Error retrieving transfer by ID: {e}")
            return make_response({'error': 'Internal server error'}, 500)

class UpdateTransfer(Resource):
    def patch(self, transfer_id):
        data = request.get_json()
        
        if not data:
            return make_response({'error': 'No data provided'}, 400)

        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return make_response({'error': 'Transfer not found'}, 404)

        try:
            updatable_fields = {
                'prescription_id': None,
                'from_pharmacy_id': None,
                'to_pharmacy_id': None,
                'patient_first_name': None,
                'patient_last_name': None,
                'patient_dob': '%Y-%m-%d',  # Date format for patient_dob
                'patient_phone_number': None,
                'medication_name': None,
                'dosage': None,
                'quantity_remaining': None,
                'refills_remaining': None,
                'prescribing_doctor': None,
                'doctor_contact': None,
                'transfer_status': self._validate_transfer_status,
                'requested_by': None,
                'requested_at': '%Y-%m-%dT%H:%M:%S',  # DateTime format
                'completed_at': '%Y-%m-%dT%H:%M:%S'   # DateTime format
            }

            for field, format_spec in updatable_fields.items():
                if field in data:
                    try:
                        if callable(format_spec):
                            # Special handling for transfer_status
                            setattr(transfer, field, format_spec(data[field]))
                        elif format_spec:
                            # Parse datetime fields
                            setattr(transfer, field, datetime.strptime(data[field], format_spec))
                        else:
                            # Regular field assignment
                            setattr(transfer, field, data[field])
                    except ValueError as e:
                        return make_response({
                            'error': f'Invalid format for {field}',
                            'expected_format': format_spec,
                            'details': str(e)
                        }, 400)

            db.session.commit()

            return make_response({
                'message': 'Transfer updated successfully',
                'transfer': transfer.to_dict()
            }, 200)

        except IntegrityError as ie:
            db.session.rollback()
            current_app.logger.error(f"Integrity Error: {ie}")
            return make_response({'error': 'Database integrity error'}, 400)
        except BadRequest as br:
            db.session.rollback()
            current_app.logger.error(f"Bad Request: {br}")
            return make_response({'error': 'Invalid request data'}, 400)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)

    def _validate_transfer_status(self, value):
        """Helper method to validate transfer status"""
        try:
            return TransferStatus(value)
        except ValueError:
            raise ValueError(f"Must be one of: {[s.value for s in TransferStatus]}")
