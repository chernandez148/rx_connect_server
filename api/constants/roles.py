"""
Centralized role definitions for the pharmacy application
"""

ROLE_HIERARCHY = {
    'SuperAdmin': 5,   # Full system access (IT/developer level)
    'PharmacyManager': 4,  # Replaces generic 'Admin' for pharmacy-specific oversight
    'Pharmacist': 3,   # Clinical authority (final verification rights)
    'Technician': 2,   # Restricted editing (no overrides)
    'Clerk': 1         # Read-only (pickup/register duties)
}

PERMISSIONS = {
    # User Management
    'view_all_users': ['SuperAdmin'],
    'view_pharmacy_users': ['SuperAdmin', 'PharmacyManager', 'Pharmacist'],
    'create_user': ['SuperAdmin', 'PharmacyManager'],
    'edit_user': ['SuperAdmin', 'PharmacyManager'],
    'delete_user': ['SuperAdmin'],  # Rarely permitted for audit purposes
    
    # Patient Data
    'add_patient': ['SuperAdmin', 'PharmacyManager', 'Pharmacist', 'Technician'],
    'view_patient': ['SuperAdmin', 'PharmacyManager', 'Pharmacist', 'Technician', 'Clerk'],
    'edit_patient': {
        'allowed_roles': ['SuperAdmin', 'PharmacyManager', 'Pharmacist', 'Technician'],
        'restricted_fields': {
            'Technician': ['dob', 'sex'],  # Requires pharmacist review
            'Pharmacist': [],  # Full access
            'PharmacyManager': []  # Full access
        }
    },
    'delete_patient': ['SuperAdmin', 'PharmacyManager'],  # Requires audit trail
    
    # Prescriptions
    'create_prescription': {
        'allowed_roles': ['Pharmacist', 'Technician'],
        'conditions': {
            'Technician': lambda rx: not rx.get('is_controlled', False)  # Block C-II-V
        }
    },
    'edit_prescription': {
        'allowed_roles': ['Pharmacist', 'Technician'],
        'conditions': {
            'Technician': lambda rx: not rx.get('is_controlled', False) and rx.get('status') != 'verified'
        }
    },
    'delete_prescription': ['Pharmacist', 'PharmacyManager'],  # Pharmacist must document reason
    
    # Transfers
    'initiate_transfer': ['Pharmacist', 'Technician'],
    'approve_transfer': ['Pharmacist'],  # Clinical judgment required
    'view_transfers': ['Pharmacist', 'Technician', 'Clerk'],
    'cancel_transfer': ['Pharmacist', 'PharmacyManager'],
    
    # System
    'view_audit_logs': ['PharmacyManager', 'SuperAdmin'],
    'export_data': ['Pharmacist', 'PharmacyManager'],  # HIPAA-protected
    'override_restrictions': ['Pharmacist']  # Emergency edits (logged)
}