from flask import request, jsonify
from burgerzilla import api, db
from flask_restx import Resource
from burgerzilla.api_models import User_Dataset, Restaurant_Dataset, Menu_Dataset, Order_Dataset, Order_Menu_Dataset, \
    Order_Menu_ID_Dataset
from burgerzilla.models import User, Restaurant, Menu, Order, Order_Menu


@api.route('/user')
class CustomerOperations(Resource):
    @api.marshal_list_with(User_Dataset, code=200, envelope='users')
    def get(self):
        all_customers = User.query.all()
        return all_customers

    @api.marshal_with(User_Dataset, code=201, envelope='user')
    def post(self):
        json_data = request.get_json()
        name = json_data.get('name')
        surname = json_data.get('surname')
        username = json_data.get('username')
        email = json_data.get('email')
        password = json_data.get('password')
        address = json_data.get('address')
        restaurant_id = json_data.get('restaurant_id')
        new_user = User(name=name, surname=surname,
                        username=username, email=email,
                        password=password, address=address, restaurant_id=restaurant_id)
        db.session.add(new_user)
        db.session.commit()
        return new_user


@api.route('/restaurant')
class RestaurantOperations(Resource):
    @api.marshal_list_with(Restaurant_Dataset, code=200, envelope='restaurants')
    def get(self):
        all_restaurants = Restaurant.query.all()
        return all_restaurants

    @api.marshal_with(Restaurant_Dataset, code=201, envelope='restaurant')
    def post(self):
        json_data = request.get_json()
        name = json_data.get('name')
        new_restaurant = Restaurant(name=name)
        db.session.add(new_restaurant)
        db.session.commit()
        return new_restaurant


@api.route('/menu')
class MenuOperations(Resource):
    @api.marshal_list_with(Menu_Dataset, code=200, envelope='menus')
    def get(self):
        all_menus = Menu.query.all()
        return all_menus

    @api.marshal_with(Menu_Dataset, code=201, envelope='menu')
    def post(self):
        json_data = request.get_json()
        product = json_data.get('product')
        price = json_data.get('price')
        description = json_data.get('description')
        image = json_data.get('image')
        restaurant_id = json_data.get('restaurant_id')
        new_menu = Menu(product=product, price=price, description=description, image=image, restaurant_id=restaurant_id)
        db.session.add(new_menu)
        db.session.commit()
        return new_menu


@api.route('/order')
class OrderOperations(Resource):
    @api.marshal_list_with(Order_Dataset, code=200, envelope='orders')
    def get(self):
        all_orders = Order.query.all()
        return all_orders

    @api.marshal_with(Order_Dataset, code=201, envelope='order')
    def post(self):
        json_data = request.get_json()
        name = json_data.get('name')
        price = json_data.get('price')
        quantity = json_data.get('quantity')
        status = json_data.get('status')
        restaurant_id = json_data.get('restaurant_id')
        user_id = json_data.get('user_id')
        new_order = Order(name=name, price=price, quantity=quantity, status=status, restaurant_id=restaurant_id,
                          user_id=user_id)
        db.session.add(new_order)
        db.session.commit()
        return new_order


@api.route('/order/<int:id>')
class OrderMenuOperations(Resource):
    @api.marshal_list_with(Order_Menu_ID_Dataset, code=200, envelope='order_menu')
    def get(self, id):
        menus = Order_Menu.query.filter_by(order_id=id)
        menu_list = []
        for each in menus:
            menu_list.append(each)

        return menu_list

    @api.marshal_with(Order_Menu_Dataset, code=201, envelope='order_menu')
    def post(self, id):
        json_data = request.get_json()
        menu_id = json_data.get('menu_id')
        new_body = Order_Menu(menu_id=menu_id, order_id=id)
        db.session.add(new_body)
        db.session.commit()
        return new_body
