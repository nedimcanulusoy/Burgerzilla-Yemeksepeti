from flask import request
from burgerzilla import api, db
from flask_restx import Resource
from burgerzilla.api_models import Response_Message, User_Dataset
from burgerzilla.models import User

@api.route('/register')
class Register(Resource):
    @api.marshal_with(Response_Message, code=201, envelope='user')
    def post(self):

        json_data = request.get_json()
        username = json_data.get('username')
        email = json_data.get('email')

        username_exists = db.session.query(User).filter_by(username=username).first() is not None
        email_exists = db.session.query(User).filter_by(email=email).first() is not None


        if not username_exists and not email_exists:
            name = json_data.get('name')
            surname = json_data.get('surname')
            password = json_data.get('password')
            address = json_data.get('address')
            restaurant_id = json_data.get('restaurant_id') or None
            new_user = User(name=name, surname=surname,
                            username=username, email=email,
                            password=password, address=address, restaurant_id=restaurant_id)

            db.session.add(new_user)
            db.session.commit()
            return {"Message": "User successfully added!"}

        else:
            return {"Message": "This username and email are already taken, try another one!"}