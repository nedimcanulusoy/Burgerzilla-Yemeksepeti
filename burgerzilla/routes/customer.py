from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, marshal

from burgerzilla import db, auth_header
from burgerzilla.api_models import (Order_Dataset, Order_Menu_ID_Dataset,
                                    New_Order_Dataset, Order_Detail_Dataset, Response_Message, Restaurant_ID_Dataset,
                                    Order_ID_Dataset)
from burgerzilla.models import User, Menu, Order, Order_Menu
from burgerzilla.routes import customer_ns


@customer_ns.route('/order')
class OrderOperations(Resource):
    @jwt_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={201: "Success", 404: "Order Not Found"})
    @customer_ns.response(model=Order_Detail_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=404, description="Not found")
    def get(self):
        """Returns the detail of the existing cart (which is order)"""

        user_id = get_jwt_identity()
        order = Order.query.filter_by(status='NEW', user_id=user_id).first()

        try:
            if order == None:
                customer_ns.logger.info('No valid order: at OrderOperations')
                return {"Message": "There is no valid order!"}, 404

            user = User.query.get(user_id)

            menus = Order_Menu.query.filter_by(order_id=order.id)
            item_list = []
            price = 0

            for menu in menus:
                item = Menu.query.get(menu.menu_id)

                price += item.price

                item_list.append(item)

            customer_ns.logger.info('GET request was `successful` at OrderOperations')
            return marshal({"name": user.name, 'address': user.address, 'timestamp': order.timestamp, 'user_id': user_id,
                            'restaurant_id': order.restaurant_id, "menus": item_list, "sum_price": price},
                           Order_Detail_Dataset), 201

        except Exception as e:
            customer_ns.logger.debug('GET request was `unsuccessful` at OrderOperations')
            return {"Message": f"An error occurred! {e}"}


    @jwt_required()
    @customer_ns.doc(body=Restaurant_ID_Dataset, security="apiKey", params=auth_header,
                     responses={201: "Success", 404: "Order Not Found"})
    @customer_ns.response(model=New_Order_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=422, description="Bad request")
    def post(self):
        """Opens the order cart (which is order) under the restaurant"""
        user_id = get_jwt_identity()
        json_data = request.json
        restaurant_id = json_data.get('restaurant_id')
        user = User.query.get(user_id)

        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()
        order_exists = order is not None

        try:
            if order_exists:
                customer_ns.logger.info('Valid active order: at OrderOperations')
                return {"Message": "You already have an active order!"}, 422

            new_order = Order(status="NEW", restaurant_id=restaurant_id,
                              user_id=user_id)

            db.session.add(new_order)
            db.session.commit()
            customer_ns.logger.info('POST request was `successful` at OrderOperations')
            return marshal(
                {"status": new_order.status, "restaurant_id": new_order.restaurant_id, "user_id": new_order.user_id},
                New_Order_Dataset), 201

        except Exception as e:
            customer_ns.logger.debug('POST request was `unsuccessful` at OrderOperations')
            return {"Message": f"An error occurred! {e}"}

@customer_ns.route('/orders')
class ListOrders(Resource):
    @jwt_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
    @customer_ns.marshal_list_with(Order_Dataset, code=200)
    def get(self):
        """Returns all orders of the user from the beginning"""
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=user_id)

        try:
            ordersList = []

            for order in orders:
                ordersList.append(order)

            customer_ns.logger.info('POST request was `successful` at ListOrders')
            return ordersList, 200

        except Exception as e:
            customer_ns.logger.debug('GET request was `unsuccessful` at ListOrders')
            return {"Message": f"An error occurred! {e}"}


@customer_ns.route('/order/delete')
class OrderDelete(Resource):
    @jwt_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found", 401:"Unauthorized", 422:"Unprocessable Entity"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Delete order (which is order cart) based on its status"""
        user_id = get_jwt_identity()
        json_data = request.json

        order_id = json_data.get("order_id")

        order = db.session.query(Order).get(order_id)
        order_exists = order is not None

        try:
            if not order_exists:
                customer_ns.logger.info('Order not exists: at OrderDelete')
                return {"Message": "This order can not be deleted!"}, 422

            if order.user_id != user_id:
                customer_ns.logger.info('Order access attempt by unauthorized user OrderDelete')
                return {"Message": "This order is not yours!"}, 401

            if order.status != "NEW" and "PENDING" and "DELETED":
                customer_ns.logger.info('Attempt to delete unavailable order status OrderDelete')
                return {"Message": "This order can not be deleted at this status!"}, 422

            db.session.query(Order).filter_by(id=order_id).update({'status': 'DELETED'})
            db.session.commit()

            customer_ns.logger.info('Successful deletion: at OrderDelete')
            return {"Message": "Order successfully deleted!"}, 200

        except Exception as e:
            customer_ns.logger.debug('POST request was `unsuccessful` at OrderDelete')
            return {"Message": f"An error occurred! {e}"}

@customer_ns.route('/order/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found", 401:"Unauthorized", 422:"Unprocessable Entity"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Cancel order (which is order cart) based on order status"""
        user_id = get_jwt_identity()
        json_data = request.json

        order_id = json_data.get("order_id")
        order = db.session.query(Order).get(order_id)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        try:
            if not order_exists:
                customer_ns.logger.info('Order not exists: at OrderCancel')
                return {"Message": "This order can not be cancelled!"}, 422

            if order.user_id != user_id:
                customer_ns.logger.info('Order access attempt by unauthorized user OrderCancel')
                return {"Message": "This order is not yours!"}, 401

            if order.status != "NEW" and "PENDING":
                customer_ns.logger.info('Attempt to delete unavailable order status OrderCancel')
                return {"Message": "This order can not be cancelled at this status!"}, 422

            db.session.query(Order).filter_by(id=order_id).update({'status': 'CUSTOMER_CANCELLED'})
            db.session.commit()

            customer_ns.logger.info('Successful cancellation: at OrderCancel')
            return {"Message": "Your order has been cancelled!"}, 200

        except Exception as e:
            customer_ns.logger.debug('POST request was `unsuccessful` at OrderCancel')
            return {"Message": f"An error occurred! {e}"}


@customer_ns.route('/order/menu')
class OrderMenuOperations(Resource):
    @jwt_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Not Found"})
    @customer_ns.marshal_list_with(Order_Menu_ID_Dataset, code=200, envelope='order_menu')
    def get(self):
        '''Returns how many menus have been ordered by the user'''
        user_id = get_jwt_identity()

        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        try:
            if not order_exists:
                customer_ns.logger.info('Order not exists: at OrderMenuOperations')
                return {"Message": "You do not have any order!"}, 404

            menus = Order_Menu.query.filter_by(order_id=order.id)
            menu_list = []
            for each in menus:
                menu_list.append(each)

            customer_ns.logger.info('GET request was `successful` at OrderMenuOperations')
            return menu_list, 200

        except Exception as e:
            customer_ns.logger.debug('GET request was `unsuccessful` at OrderMenuOperations')
            return {"Message": f"An error occurred! {e}"}

    @jwt_required()
    @customer_ns.doc(body=Order_Menu_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Not Found"})
    @customer_ns.marshal_with(Response_Message, code=201, envelope='order_menu')
    def post(self):
        '''Add menu to order of the user'''
        user_id = get_jwt_identity()
        json_data = request.get_json()
        menu_id = json_data.get('menu_id')

        order_id = db.session.query(Order).filter_by(user_id=user_id, status="NEW").first().id

        try:
            add_menu = Order_Menu(menu_id=menu_id, order_id=order_id)
            db.session.add(add_menu)
            db.session.commit()
            customer_ns.logger.info('POST request was `successful` at OrderMenuOperations')
            return {'Message': "Menu successfully added to your order!"}, 201
        except:
            customer_ns.logger.debug('POST request was `unsuccessful` at OrderMenuOperations')
            return {'Message': "Unfortunately the menu could not be added to your order, try again!"}
