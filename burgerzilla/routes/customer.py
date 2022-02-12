from flask import request
from burgerzilla import db, auth_header
from flask_restx import Resource, marshal
from burgerzilla.api_models import (Order_Dataset, Order_Menu_ID_Dataset,
                                    New_Order_Dataset, Order_Detail_Dataset, Response_Message, Restaurant_ID_Dataset,
                                    Order_ID_Dataset)
from burgerzilla.models import User, Menu, Order, Order_Menu
from flask_jwt_extended import jwt_required, get_jwt_identity

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

        if order == None:
            return {"Message": "There is no valid order!"}, 404

        user = User.query.get(user_id)

        menus = Order_Menu.query.filter_by(order_id=order.id)
        item_list = []
        price = 0

        for menu in menus:
            item = Menu.query.get(menu.menu_id)

            price += item.price

            item_list.append(item)

        return {"name": user.name, 'address': user.address, 'timestamp': order.timestamp, 'user_id': user_id,
                'restaurant_id': order.restaurant_id, "menus": item_list, "sum_price": price}, 200

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

        if order_exists:
            return {"Message": "You already have an active order!"}, 422

        new_order = Order(status="NEW", restaurant_id=restaurant_id,
                          user_id=user_id)

        db.session.add(new_order)
        db.session.commit()
        return marshal(
            {"status": new_order.status, "restaurant_id": new_order.restaurant_id, "user_id": new_order.user_id},
            New_Order_Dataset), 201


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
        ordersList = []

        for order in orders:
            ordersList.append(order)

        return ordersList


@customer_ns.route('/order/delete')
class OrderDelete(Resource):
    @jwt_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Delete order (which is order cart) based on its status"""
        user_id = get_jwt_identity()
        json_data = request.json

        order_id = json_data.get("order_id")

        order = db.session.query(Order).get(order_id)
        order_exists = order is not None

        if not order_exists:
            return {"Message": "This order can not be deleted!"}, 422

        if order.user_id != user_id:
            return {"Message": "This order is not yours!"}, 401

        if order.status != "NEW" and "PENDING" and "DELETED":
            return {"Message": "This order can not be deleted at this status!"}, 422

        db.session.query(Order).filter_by(id=order_id).update(
            {'status': 'DELETED'})
        db.session.commit()

        return {"Message": "Order successfully deleted!"}, 200


@customer_ns.route('/order/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @customer_ns.doc(body=Order_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        """Cancel order (which is order cart) based on order status"""
        user_id = get_jwt_identity()
        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        if not order_exists:
            return {"Message": "There is no available order!"}, 404

        order_id = order.id

        db.session.query(Order).filter_by(id=order_id).update(
            {'status': 'CANCELLED'})
        db.session.commit()

        return {"Message": "Your order has been cancelled!"}, 200


@customer_ns.route('/order/menu')
class OrderMenuOperations(Resource):
    @jwt_required()
    @customer_ns.doc(security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
    @customer_ns.marshal_list_with(Order_Menu_ID_Dataset, code=200, envelope='order_menu')
    def get(self):
        '''Returns how many menus have been ordered by the user'''
        user_id = get_jwt_identity()

        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        if not order_exists:
            return {"Message": "You do not have any order!"}, 422

        menus = Order_Menu.query.filter_by(order_id=order.id)
        menu_list = []
        for each in menus:
            menu_list.append(each)

        return menu_list

    @jwt_required()
    @customer_ns.doc(body=Order_Menu_ID_Dataset, security="apiKey", params=auth_header,
                     responses={200: "Success", 404: "Order Not Found"})
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
            return {'Message': "Menu successfully added to your order!"}
        except:
            return {'Message': "Unfortunately the menu could not be added to your order, try again!"}
