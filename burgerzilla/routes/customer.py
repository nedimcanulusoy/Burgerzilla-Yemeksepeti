from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, marshal

from burgerzilla import db, auth_header
from burgerzilla.api_models import (Order_Dataset, Order_Menu_ID_Dataset,
                                    New_Order_Dataset, Order_Detail_Dataset, Response_Message, Restaurant_ID_Dataset,
                                    Order_ID_Dataset)
from burgerzilla.models import User, Menu, Order, Order_Menu
from burgerzilla.order_status import OrderStatus
from burgerzilla.routes import customer_ns
from burgerzilla.routes.utils import customer_required


@customer_ns.route('/order')
class OrderOperations(Resource):
    @jwt_required()
    @customer_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={201: "Success", 404: "Order Not Found"})
    @customer_ns.response(model=Order_Detail_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=404, description="Not found")
    def get(self):
        """Returns details of current order basket if exists"""

        user_id = get_jwt_identity()
        order = Order.query.filter_by(status=OrderStatus.NEW, user_id=user_id).first()
        order_exists = order is not None

        if not order_exists:
            customer_ns.logger.info('No valid order: at OrderOperations')
            return {"Message": "There is no active order basket!"}, 404

        user = User.query.get(user_id)

        order_menus = Order_Menu.query.filter_by(order_id=order.id)
        menus = []
        price = 0

        for order_menu in order_menus:
            menu = Menu.query.get(order_menu.menu_id)

            price += menu.price

            menus.append(menu)

        customer_ns.logger.info('GET request was `successful` at OrderOperations')

        return marshal({
            "id": order.id,
            "name": user.name,
            'address': user.address,
            'timestamp': order.timestamp,
            'user_id': user_id,
            'restaurant_id': order.restaurant_id,
            "menus": menus,
            "sum_price": price
        }, Order_Detail_Dataset), 201

    @jwt_required()
    @customer_required()
    @customer_ns.doc(body=Restaurant_ID_Dataset, security="apiKey", params=auth_header,
                     responses={201: "Success", 404: "Order Not Found"})
    @customer_ns.response(model=New_Order_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=422, description="Bad request")
    def post(self):
        """Creates a new order basket if not exists any new"""
        user_id = get_jwt_identity()
        json_data = request.json
        restaurant_id = json_data.get('restaurant_id')

        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == OrderStatus.NEW).first()
        order_exists = order is not None

        if order_exists:
            customer_ns.logger.info('Valid active order: at OrderOperations')
            return {"Message": "You already have an active order basket!"}, 422

        new_order = Order(status=OrderStatus.NEW, restaurant_id=restaurant_id,
                          user_id=user_id)

        db.session.add(new_order)
        db.session.commit()

        customer_ns.logger.info('POST request was `successful` at OrderOperations')

        return marshal({
            "status": new_order.status,
            "restaurant_id": new_order.restaurant_id,
            "user_id": new_order.user_id
        }, New_Order_Dataset), 201


@customer_ns.route('/orders')
class ListOrders(Resource):
    @jwt_required()
    @customer_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
    @customer_ns.marshal_list_with(Order_Dataset, code=200)
    def get(self):
        """Returns order history of customer"""
        user_id = get_jwt_identity()
        orders = db.session.query(Order).filter(Order.user_id == user_id, Order.status != OrderStatus.DELETED).all()

        customer_ns.logger.info('POST request was `successful` at ListOrders')

        return orders, 200


@customer_ns.route('/order/delete')
class OrderDelete(Resource):
    @jwt_required()
    @customer_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found", 401: "Unauthorized",
                                422: "Unprocessable Entity"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Deletes order from customer's history"""
        user_id = get_jwt_identity()
        json_data = request.json

        order_id = json_data.get("order_id")

        order = db.session.query(Order).get(order_id)
        order_exists = order is not None

        if not order_exists:
            customer_ns.logger.info('Order not exists: at OrderDelete')
            return {"Message": "This order can not be deleted!"}, 422

        if order.user_id != user_id:
            customer_ns.logger.info('Order access attempt by unauthorized user OrderDelete')
            return {"Message": "This order is not yours!"}, 401

        if order.status != OrderStatus.NEW and OrderStatus.PENDING and OrderStatus.DONE:
            customer_ns.logger.info('Attempt to delete unavailable order status OrderDelete')
            return {"Message": "This order can not be deleted at this status!"}, 422

        db.session.query(Order).filter_by(id=order_id).update({'status': OrderStatus.DELETED})
        db.session.commit()

        customer_ns.logger.info('Successful deletion: at OrderDelete')

        return {"Message": "Order successfully deleted!"}, 200


@customer_ns.route('/order/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @customer_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found", 401: "Unauthorized",
                                422: "Unprocessable Entity"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Cancels current order basket if exists"""
        user_id = get_jwt_identity()
        json_data = request.json

        order_id = json_data.get("order_id")
        order = db.session.query(Order).get(order_id)
        order_exists = order is not None

        if not order_exists:
            customer_ns.logger.info('Order not exists: at OrderCancel')
            return {"Message": "This order can not be cancelled!"}, 422

        if order.user_id != user_id:
            customer_ns.logger.info('Order access attempt by unauthorized user OrderCancel')
            return {"Message": "This order is not yours!"}, 401

        if order.status != OrderStatus.NEW and OrderStatus.PENDING:
            customer_ns.logger.info('Attempt to delete unavailable order status OrderCancel')
            return {"Message": "This order can not be cancelled at this status!"}, 422

        db.session.query(Order).filter_by(id=order_id).update({'status': OrderStatus.CUSTOMER_CANCELLED})
        db.session.commit()

        customer_ns.logger.info('Successful cancellation: at OrderCancel')
        return {"Message": "Your order has been cancelled!"}, 200


@customer_ns.route('/order/menu/add')
class OrderMenuOperations(Resource):

    @jwt_required()
    @customer_required()
    @customer_ns.doc(body=Order_Menu_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Not Found"})
    @customer_ns.marshal_with(Response_Message, code=201)
    def post(self):
        """Adds specified menu to current order basket if exists"""
        user_id = get_jwt_identity()
        json_data = request.get_json()
        menu_id = json_data.get('menu_id')

        order = db.session.query(Order).filter_by(user_id=user_id, status=OrderStatus.NEW).first()
        order_exists = order is not None

        if not order_exists:
            return {"Message": "You don't have an active order basket!"}, 404

        menu = db.session.query(Menu).get(menu_id)
        menu_exists = menu is not None

        if not menu_exists:
            return {"Message": "This menu is not exists!"}, 404

        new_menu = Order_Menu(menu_id=menu_id, order_id=order.id)

        db.session.add(new_menu)
        db.session.commit()

        customer_ns.logger.info('POST request was `successful` at OrderMenuOperations')

        return {'Message': "Menu successfully added to your order!"}, 201


@customer_ns.route('/order/menu/remove')
class RemoveOrderMenuFromOrder(Resource):
    @jwt_required()
    @customer_required()
    @customer_ns.doc(body=Order_Menu_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Not Found"})
    @customer_ns.marshal_with(Response_Message, code=201)
    def post(self):
        """Removes specific menu from current order basket if exists"""
        user_id = get_jwt_identity()
        json_data = request.get_json()
        menu_id = json_data.get('menu_id')

        order = db.session.query(Order).filter_by(user_id=user_id, status=OrderStatus.NEW).first()
        order_exists = order is not None

        if not order_exists:
            return {"Message": "You don't have an active order basket!"}, 404

        order_menu = db.session.query(Order_Menu).filter(Order_Menu.menu_id == menu_id,
                                                         Order_Menu.order_id == order.id).first()
        order_menu_exists = order_menu is not None

        if not order_menu_exists:
            return {"Message": "This menu is not exists in your order basket!"}, 404

        db.session.delete(order_menu)
        db.session.commit()

        customer_ns.logger.info('POST request was `successful` at OrderMenuOperations')

        return {'Message': "Menu successfully removed from your order!"}, 201
