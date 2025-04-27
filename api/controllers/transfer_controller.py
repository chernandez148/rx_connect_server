from flask import request, current_app, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models.transfers import Transfer, TransferStatus
from models.pharmacies import Pharmacy
from config import db


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

        transfer = Transfer.query.get(transfer_id)
        if not transfer:
            return make_response({'error': 'Transfer not found'}, 404)

        try:
            # List of fields that are allowed to be updated
            updatable_fields = [
                'prescription_id',
                'from_pharmacy_id',
                'to_pharmacy_id',
                'patient_first_name',
                'patient_last_name',
                'patient_dob',
                'patient_phone_number',
                'medication_name',
                'dosage',
                'quantity_remaining',
                'refills_remaining',
                'prescribing_doctor',
                'doctor_contact',
                'transfer_status',
                'requested_by',
                'requested_at',
                'completed_at'
            ]

            for field in updatable_fields:
                if field in data:
                    if field == 'patient_dob':
                        setattr(transfer, field, datetime.strptime(data[field], '%Y-%m-%d'))
                    elif field in ['requested_at', 'completed_at']:
                        setattr(transfer, field, datetime.strptime(data[field], '%Y-%m-%dT%H:%M:%S'))
                    elif field == 'transfer_status':
                        try:
                            setattr(transfer, field, TransferStatus(data[field]))
                        except ValueError:
                            return make_response({'error': f"Invalid transfer_status. Must be one of: {[s.value for s in TransferStatus]}"}, 400)
                    else:
                        setattr(transfer, field, data[field])

            db.session.commit()

            return make_response({
                'message': 'Transfer updated successfully',
                'transfer': transfer.to_dict()
            }, 200)

        except IntegrityError as ie:
            db.session.rollback()
            current_app.logger.error(f"Integrity Error: {ie}")
            return make_response({'error': 'Integrity constraint violated'}, 400)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected Error: {e}")
            return make_response({'error': 'Internal server error'}, 500)
