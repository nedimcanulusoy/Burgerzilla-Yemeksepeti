from flask import request
from burgerzilla import api, db, jwt
from flask_restx import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required
from burgerzilla.api_models import JWT_Dataset, Response_Message
from burgerzilla.models import User, TokenBlocklist
from datetime import datetime, timedelta, timezone

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

@api.route('/login')
class AuthLogin(Resource):
    @api.marshal_with(JWT_Dataset, Response_Message)
    def post(self):
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

@api.route('/logout')
class AuthLogout(Resource):
    @jwt_required()
    @api.marshal_with(Response_Message)
    def post(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return {"Message":"Logged out and JWT revoked"}
