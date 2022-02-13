from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, marshal

from burgerzilla import db, auth_header
from burgerzilla.api_models import (Restaurant_Dataset, Menu_Dataset, Restaurant_Order_Dataset, Response_Message,
                                    Order_Dataset)
from burgerzilla.models import User, Restaurant, Menu, Order, Order_Menu
from burgerzilla.routes import restaurant_ns
from burgerzilla.routes.utils import owner_required


@restaurant_ns.route('')
@restaurant_ns.doc(
    responses={200: "Success", 404: "Not Found"})
class RestaurantOperations(Resource):
    @restaurant_ns.marshal_list_with(Restaurant_Dataset, code=200, envelope='restaurants')
    def get(self):
        """Returns all restaurants"""
        all_restaurants = Restaurant.query.all()
        restaurant_ns.logger.debug('GET request was `successful` at RestaurantOperations')
        return all_restaurants



@restaurant_ns.route('/menu')
class MenuOperations(Resource):
    @jwt_required()
    @restaurant_ns.doc(body=Menu_Dataset, params=auth_header,
                       responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials",
                                  404: "Not Found"})
    @restaurant_ns.marshal_with(Menu_Dataset, code=201, envelope='menu')
    @owner_required()
    def post(self):
        """Adds a new menu to the restaurant"""
        json_data = request.get_json()
        name = json_data.get('name')
        price = json_data.get('price')
        description = json_data.get('description')
        image = json_data.get('image')
        restaurant_id = json_data.get('restaurant_id')

        new_menu = Menu(name=name, price=price, description=description, image=image, restaurant_id=restaurant_id)
        db.session.add(new_menu)
        db.session.commit()
        restaurant_ns.logger.debug('POST request was `successful` at MenuOperations')
        return new_menu


@restaurant_ns.route('/<int:id>/menu')
class GetRestaurantMenu(Resource):
    @restaurant_ns.doc(
        responses={201: "Success", 404: "Menu Not Found"})
    @restaurant_ns.marshal_list_with(Menu_Dataset, code=201, envelope='menus')
    def get(self, id):
        """Returns the menu according to the ID of the restaurant"""
        restaurant_menus = Menu.query.filter_by(restaurant_id=id).all()
        restaurant_ns.logger.debug('GET request was `successful` at GetRestaurantMenu')
        return restaurant_menus, 201


@restaurant_ns.route('/<int:id>/orders')
class RestaurantOrder(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header, responses={200: "Success", 404: "Not Found"})
    @restaurant_ns.marshal_list_with(Order_Dataset)
    def get(self, id):
        """Returns which menu order was taken"""
        orders = db.session.query(Order).filter(Order.restaurant_id == id, Order.status != "NEW").all()

        restaurant_ns.logger.debug('GET request was `successful` at RestaurantOrder')

        return orders, 200



@restaurant_ns.route('/order/<int:id>/detail')
class RestaurantOrderDetail(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header, responses={201: "Success", 404: "Not Found"})
    @restaurant_ns.response(model=Restaurant_Order_Dataset, code=201, description='restaurant_order_item_detail')
    def get(self, id):
        """Returns order details of the user to the Restaurant"""
        order = db.session.query(Order).filter(Order.status != 'NEW', Order.id == id).first()
        order_exists = order is not None

        if not order_exists:
            restaurant_ns.logger.info('No valid order: at RestaurantOrderDetail')

            return {"Error": "This order is not available at the moment!"}, 404

        user = User.query.get(order.user_id)

        order_menus = db.session.query(Order_Menu).filter(Order_Menu.order_id == order.id).all()
        menus = []
        price = 0

        for order_menu in order_menus:
            item = Menu.query.get(order_menu.menu_id)  # menu item
            price += item.price  # menu price

            menus.append(item)

        restaurant_ns.logger.debug('GET request was `successful` at RestaurantOrderDetail')

        return marshal({
            "name": user.name,
            'address': user.address,
            'timestamp': order.timestamp,
            'user_id': user.id,
            'status': order.status,
            'restaurant_id': order.restaurant_id,
            "menus": menus,
            'sum_price': price
        }, Restaurant_Order_Dataset), 201


@restaurant_ns.route('/order/<int:id>/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header, responses={200: "Success", 404: "Not Found"})
    @restaurant_ns.marshal_with(Response_Message)
    def post(self, id):
        """Cancel user's order by restaurant"""
        order = db.session.query(Order).filter(Order.id == id,
                                               Order.status == "PENDING" and "PREPARING" and "ON_THE_WAY").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None

        if not order_exists:
            restaurant_ns.logger.info('No valid order: at OrderCancel')
            return {"Message": "This order is not available to cancel!"}, 403

        db.session.query(Order).filter_by(id=id).update(
            {
                'status': 'RESTAURANT_CANCELLED'})  # Delete degil update olacak burada status icin """Statusu Cancel yap"""
        db.session.commit()

        restaurant_ns.logger.debug('POST request was `successful` at OrderCancel')

        return {"Message": "This order has been cancelled!"}, 200
