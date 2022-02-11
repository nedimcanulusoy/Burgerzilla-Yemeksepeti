from flask import request
from burgerzilla import db, jwt, auth_header
from flask_restx import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required
from burgerzilla.api_models import JWT_Dataset, Response_Message, Login_Dataset
from burgerzilla.models import User, TokenBlocklist
from datetime import datetime, timezone

from burgerzilla.routes.auth import auth


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

@auth.route('/login')
@auth.doc(body=Login_Dataset,
          responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials", 404: "User Not Found"})
class AuthLogin(Resource):
    @auth.marshal_with(JWT_Dataset, Response_Message)
    def post(self):
        """User Login"""
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')

        if not username or not password:
            return {"Message": "Username or Password missing!"}

        user = db.session.query(User).filter_by(username=username).first()
        user_exists = user is not None

        if not user_exists or not user.verify_password(password):
            return {"Message": "Your username or password is incorrect!"}

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token, "refresh_token": refresh_token,
                "Message": "The token has been successfully created!"}




@auth.route('/logout')
class AuthLogout(Resource):
    @jwt_required()
    @auth.marshal_with(Response_Message)
    def post(self):
        """User Logout"""
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return {"Message":"Logged out and JWT revoked"}
