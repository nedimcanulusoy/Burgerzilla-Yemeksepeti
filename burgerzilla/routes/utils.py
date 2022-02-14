from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from burgerzilla.models import UserRoles, Role, User

'''
A decorator on both the customer and restaurant side to restrict unauthorized actions between each other.
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

            return {"Message": "Owner only!"}, 403

        return decorator

    return wrapper


def customer_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()  # Get user id from JWT
            # Get user roles
            user_roles = UserRoles.query.filter_by(user_id=user_id).all()

            is_owner = False  # Set default as False

            for user_role in user_roles:
                role = Role.query.get(user_role.role_id)  # Query for Roles table to check roles

                if role.name == "Owner":  # Check is user an owner
                    is_owner = True  # Set is_owner true

            if not is_owner:  # If user is not an owner continue
                return fn(*args, **kwargs)

            return {"Message": "Customer only!"}, 403

        return decorator

    return wrapper


def validate_owner_restaurant():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()  # Get user id from JWT

            # Get user from user table
            user = User.query.get(user_id)

            # Check if this user matches with its restaurant
            if user.restaurant_id == kwargs.get("restaurant_id"):
                return fn(*args, **kwargs)

            return {"Message": "You don't have access to this restaurant!"}, 403

        return decorator

    return wrapper
