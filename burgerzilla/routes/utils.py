from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from burgerzilla.models import UserRoles, Role

'''
A decorator on the restaurant side to restrict unauthorized actions by other non-owners users
'''


def owner_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()  # Get user id from JWT
            # Query for UserRoles table to check if current user is in the table or not
            user_roles = UserRoles.query.filter_by(user_id=user_id).all()

            is_owner = False  # Set default as False

            for user_role in user_roles:
                role = Role.query.get(user_role.role_id)  # Query for Roles table to check roles

                if role.name == "Owner":  # Set role for user
                    is_owner = True  # Change default value as True

            if is_owner:
                return fn(*args, **kwargs)

            return jsonify(msg="Owner only!"), 403

        return decorator

    return wrapper