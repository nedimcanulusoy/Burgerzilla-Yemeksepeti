from random import random

from flask import request
from burgerzilla import api, db
from flask_restx import Resource
from burgerzilla.api_models import Response_Message, User_Dataset
from burgerzilla.models import User, Role, Restaurant


@api.route('/register')
class Register(Resource):
    @api.marshal_with(Response_Message, code=201, envelope='user')
    def post(self):

        json_data = request.json
        name = json_data.get('name')
        surname = json_data.get('surname')
        username = json_data.get('username')
        email = json_data.get('email')
        password = json_data.get('password')
        address = json_data.get('address')
        is_owner = json_data.get('is_owner') or False
        restaurant = json_data['restaurant']

        username_exists = db.session.query(User).filter_by(username=username).first() is not None
        email_exists = db.session.query(User).filter_by(email=email).first() is not None

        if username_exists or email_exists:
            return {"Message": "This username or email is already taken, try another one!"}

        if not is_owner:
            restaurant_id = None

        if is_owner:
            new_restaurant = Restaurant(name=restaurant['name'])
            db.session.add(new_restaurant)
            db.session.commit()
            
            restaurant_id = new_restaurant.id

        new_user = User(
            name=name,
            surname=surname,
            username=username,
            email=email,
            password=password,
            address=address,
            restaurant_id=restaurant_id
        )

        if is_owner:
            role = Role.query.filter_by(name='Owner').first() or Role(name='Owner')
            new_user.roles.append(role)
            

        db.session.add(new_user)
        db.session.commit()
        return {"Message": "User successfully registered!"}
