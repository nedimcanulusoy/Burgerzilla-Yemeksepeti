from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timezone

from burgerzilla import auth_header, db
from burgerzilla.api_models import Response_Message
from burgerzilla.models import TokenBlocklist
from burgerzilla.routes import auth_ns


@auth_ns.route('/logout')
class AuthLogout(Resource):
    @jwt_required()
    @auth_ns.marshal_with(Response_Message)
    @auth_ns.doc(security="apiKey", params={**auth_header},
                 responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials",
                            404: "Token Not Found"})
    def post(self):
        """User Logout"""
        try:
            jti = get_jwt()["jti"]
            now = datetime.now(timezone.utc)

            db.session.add(TokenBlocklist(jti=jti, created_at=now))
            db.session.commit()

            auth_ns.logger.info('User successfully logged out and JWT revoked at AuthLogout!')

            return {"Message": "Logged out and JWT revoked"}

        except Exception as e:
            auth_ns.logger.debug("An error occurred while logging out at AuthLogout!")
            return {"Message": f"An error occurred! {e}"}
