from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restx import Resource

from burgerzilla import db, jwt
from burgerzilla.api_models import JWT_Dataset, Response_Message, Login_Dataset
from burgerzilla.models import User, TokenBlocklist
from burgerzilla.routes import auth_ns


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


@auth_ns.route('/login')
class AuthLogin(Resource):
    @auth_ns.doc(body=Login_Dataset,
                 responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials"})
    @auth_ns.marshal_with(JWT_Dataset, Response_Message)
    def post(self):
        """User Login"""
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')

        if not username or not password:
            auth_ns.logger.debug('Missing Username or Password at AuthLogin: %s', username)
            return {"Message": "Username or Password missing!"}, 400

        user = db.session.query(User).filter_by(username=username).first()
        user_exists = user is not None

        if not user_exists or not user.verify_password(password):
            auth_ns.logger.debug('Wrong Username or Password attempt at AuthLogin: %s', username)
            return {"Message": "Your username or password is incorrect!"}, 403

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        auth_ns.logger.info('User successfully logged in at AuthLogin: %s', username)

        return {"access_token": access_token, "refresh_token": refresh_token,
                "Message": "The token has been successfully created!"}, 200
