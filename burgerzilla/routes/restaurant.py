from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, marshal

from burgerzilla import db, auth_header
from burgerzilla.api_models import (Menu_Dataset, Restaurant_Order_Dataset, Response_Message,
                                    Order_Dataset, Update_Order_Status)
from burgerzilla.models import User, Menu, Order, Order_Menu
from burgerzilla.order_status import OrderStatus
from burgerzilla.routes import restaurant_ns
from burgerzilla.routes.utils import owner_required, validate_owner_restaurant


@restaurant_ns.route('/menu')
class MenuOperations(Resource):
    @jwt_required()
    @restaurant_ns.doc(body=Menu_Dataset, params=auth_header,
                       responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials",
                                  404: "Not Found"})
    @restaurant_ns.marshal_with(Menu_Dataset, code=201, envelope='menu')
    @owner_required()
    @validate_owner_restaurant()
    def post(self, restaurant_id):
        """Adds a new menu to the restaurant"""
        json_data = request.get_json()
        name = json_data.get('name')
        price = json_data.get('price')
        description = json_data.get('description')
        image = json_data.get('image')

        new_menu = Menu(name=name, price=price, description=description, image=image, restaurant_id=restaurant_id)
        db.session.add(new_menu)
        db.session.commit()
        restaurant_ns.logger.debug('POST request was `successful` at MenuOperations')
        return new_menu


@restaurant_ns.route('/menus')
class GetRestaurantMenu(Resource):
    @restaurant_ns.doc(
        responses={201: "Success", 404: "Menu Not Found"})
    @restaurant_ns.marshal_list_with(Menu_Dataset, code=201, envelope='menus')
    def get(self, restaurant_id):
        """Returns the menu according to the ID of the restaurant"""
        restaurant_menus = Menu.query.filter_by(restaurant_id=restaurant_id).all()
        restaurant_ns.logger.debug('GET request was `successful` at GetRestaurantMenu')
        return restaurant_menus, 201


@restaurant_ns.route('/orders')
class RestaurantOrder(Resource):
    @jwt_required()
    @owner_required()
    @validate_owner_restaurant()
    @restaurant_ns.doc(params=auth_header, responses={200: "Success", 404: "Not Found"})
    @restaurant_ns.marshal_list_with(Order_Dataset)
    def get(self, restaurant_id):
        """Returns which menu order was taken"""
        orders = db.session.query(Order).filter(Order.restaurant_id == restaurant_id,
                                                Order.status != OrderStatus.NEW).all()

        restaurant_ns.logger.debug('GET request was `successful` at RestaurantOrder')

        return orders, 200


@restaurant_ns.route('/order/<int:order_id>/detail')
class RestaurantOrderDetail(Resource):
    @jwt_required()
    @owner_required()
    @validate_owner_restaurant()
    @restaurant_ns.doc(params=auth_header, responses={201: "Success", 404: "Not Found"})
    @restaurant_ns.response(model=Restaurant_Order_Dataset, code=201, description='restaurant_order_item_detail')
    def get(self, restaurant_id, order_id):
        """Returns order details of the user to the Restaurant"""
        order = db.session.query(Order).filter(Order.status != OrderStatus.NEW, Order.id == order_id).first()
        order_exists = order is not None

        if not order_exists:
            restaurant_ns.logger.info('No valid order: at RestaurantOrderDetail')

            return {"Error": "This order is not available at the moment!"}, 404

        user = User.query.get(order.user_id)

        order_menus = db.session.query(Order_Menu).filter(Order_Menu.order_id == order_id).all()
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


@restaurant_ns.route('/order/<int:order_id>/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @owner_required()
    @validate_owner_restaurant()
    @restaurant_ns.doc(params=auth_header, responses={200: "Success", 404: "Not Found"})
    @restaurant_ns.marshal_with(Response_Message)
    def post(self, restaurant_id, order_id):
        """Cancel user's order by restaurant"""
        order = db.session.query(Order).filter(Order.id == order_id,
                                               Order.status == OrderStatus.PENDING and OrderStatus.PENDING and OrderStatus.ON_THE_WAY).first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None

        if not order_exists:
            restaurant_ns.logger.info('No valid order: at OrderCancel')
            return {"Message": "This order is not available to cancel!"}, 403

        db.session.query(Order).filter_by(id=order_id).update({
            'status': OrderStatus.RESTAURANT_CANCELLED
        })  # Delete degil update olacak burada status icin """Statusu Cancel yap"""

        db.session.commit()

        restaurant_ns.logger.debug('POST request was `successful` at OrderCancel')

        return {"Message": "This order has been cancelled!"}, 200


@restaurant_ns.route('/order/<int:order_id>/status')
class UpdateOrderStatus(Resource):
    @jwt_required()
    @owner_required()
    @validate_owner_restaurant()
    @restaurant_ns.doc(body=Update_Order_Status, params=auth_header, responses={200: "Success", 404: "Not Found"})
    @restaurant_ns.marshal_with(Response_Message)
    def put(self, restaurant_id, order_id):
        json_data = request.get_json()
        status = json_data.get("status")

        order = Order.query.get(order_id)
        order_exists = order is not None

        if not order_exists:
            return {"Message": "This order is not exists!"}, 404

        not_allowed_statuses = ["NEW", "CUSTOMER_CANCELLED", "DELETED"]
        status_valid = False

        for order_status in OrderStatus:
            if status == order_status:
                status_valid = True

        if status in not_allowed_statuses:
            status_valid = False

        if not status_valid:
            return {"Message": "This status is not valid!"}, 422

        order.status = status
        db.session.commit()

        return {"Message": "Order status has successfully changed!"}, 200
