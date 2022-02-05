from flask import request, jsonify
from burgerzilla import api, db
from flask_restx import Resource
from burgerzilla.api_models import Customer_Dataset, Owner_Dataset, Restaurant_Dataset, Menu_Dataset, Order_Dataset
from burgerzilla.models import Customer, Owner, Restaurant, Menu, Order


@api.route('/customer')
class CustomerOperations(Resource):
    @api.marshal_list_with(Customer_Dataset, code=200, envelope='customers')
    def get(self):
        all_customers = Customer.query.all()
        return all_customers

    @api.marshal_with(Customer_Dataset, code=201, envelope='customer')
    def post(self):
        json_data = request.get_json()
        customer_name = json_data.get('customer_name')
        customer_surname = json_data.get('customer_surname')
        customer_username = json_data.get('customer_username')
        customer_email = json_data.get('customer_email')
        customer_password = json_data.get('customer_password')
        customer_address = json_data.get('customer_address')
        new_customer = Customer(customer_name=customer_name, customer_surname=customer_surname,
                                customer_username=customer_username, customer_email=customer_email,
                                customer_password=customer_password, customer_address=customer_address)
        db.session.add(new_customer)
        db.session.commit()
        return new_customer


@api.route('/owner')
class OwnerOperations(Resource):
    @api.marshal_list_with(Owner_Dataset, code=200, envelope='owners')
    def get(self):
        all_owners = Owner.query.all()
        return all_owners

    @api.marshal_with(Owner_Dataset, code=201, envelope='owner')
    def post(self):
        json_data = request.get_json()
        owner_name = json_data.get('owner_name')
        owner_surname = json_data.get('owner_surname')
        owner_username = json_data.get('owner_username')
        owner_email = json_data.get('owner_email')
        owner_password = json_data.get('owner_password')
        owner_address = json_data.get('owner_address')
        new_owner = Owner(owner_name=owner_name, owner_surname=owner_surname,
                          owner_username=owner_username, owner_email=owner_email,
                          owner_password=owner_password, owner_address=owner_address)
        db.session.add(new_owner)
        db.session.commit()
        return new_owner


@api.route('/restaurant')
class RestaurantOperations(Resource):
    @api.marshal_list_with(Restaurant_Dataset, code=200, envelope='restaurants')
    def get(self):
        all_restaurants = Restaurant.query.all()
        return all_restaurants

    @api.marshal_with(Restaurant_Dataset, code=201, envelope='restaurant')
    def post(self):
        json_data = request.get_json()
        restaurant_name = json_data.get('restaurant_name')
        restaurant_owner = json_data.get('restaurant_owner')
        new_restaurant = Restaurant(restaurant_name=restaurant_name,restaurant_owner=restaurant_owner)
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
        restaurant_menu = json_data.get('restaurant_menu')
        new_menu = Menu(product=product, price=price, description=description, image=image, restaurant_menu=restaurant_menu)
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
        order_name = json_data.get('order_name')
        order_price = json_data.get('order_price')
        order_quantity = json_data.get('order_quantity')
        order_accept_cancel = json_data.get('order_accept_cancel')
        order_status = json_data.get('order_status')
        order_customer = json_data.get('order_customer')
        order_restaurant = json_data.get('order_restaurant')
        new_order = Order(order_name=order_name, order_price=order_price, order_quantity=order_quantity,
                          order_accept_cancel=order_accept_cancel, order_status=order_status, order_customer=order_customer,
                          order_restaurant=order_restaurant)
        db.session.add(new_order)
        db.session.commit()
        return new_order
