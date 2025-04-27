# models/__init__.py
from config import db

from .pharmacies import Pharmacy
from .patients import Patient
from .users import User
from .prescriptions import Prescription
from .pharmacy_patients import PharmacyPatients
from .pharmacy_prescriptions import PharmacyPrescription

# Import other models here

__all__ = ['Pharmacy', 'Patient', 'User', 'Prescription', 'PharmacyPatients' ,'PharmacyPrescription']