from functools import wraps
from flask import abort, current_app, g, request
from api.constants.roles import PERMISSIONS, ROLE_HIERARCHY
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from models import User
from datetime import datetime

def requires_permission(permission_name):
    """Enhanced role-based permission decorator with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify JWT and get user
            verify_jwt_in_request()
            jwt_data = get_jwt()
            user_id = jwt_data.get('sub')
            
            # Fetch user with role and active status
            current_user = User.query.filter_by(id=user_id).first()
            if not current_user or not current_user.is_active:
                current_app.logger.warning(f"Unauthorized access attempt by inactive user {user_id}")
                abort(403, "Account inactive or invalid")
            
            # Check permission structure
            permission = PERMISSIONS.get(permission_name)
            if not permission:
                current_app.logger.error(f"Undefined permission: {permission_name}")
                abort(500, "Server configuration error")
            
            # Handle simple list permissions
            if isinstance(permission, list):
                if current_user.role not in permission:
                    current_app.logger.warning(
                        f"Permission denied for {current_user.role} on {permission_name}"
                    )
                    abort(403, "Insufficient privileges")
            
            # Handle complex permission with conditions
            elif isinstance(permission, dict):
                allowed_roles = permission.get('allowed_roles', [])
                
                if current_user.role not in allowed_roles:
                    current_app.logger.warning(
                        f"Role {current_user.role} not in allowed roles for {permission_name}"
                    )
                    abort(403, "Insufficient privileges")
                
                # Add restricted fields to kwargs if specified
                if 'restricted_fields' in permission:
                    kwargs['restricted_fields'] = permission['restricted_fields'].get(
                        current_user.role, []
                    )
            
            # Log the access
            current_app.logger.info(
                f"User {current_user.id} ({current_user.role}) accessed "
                f"{request.method} {request.path} with {permission_name}"
            )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator