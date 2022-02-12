from flask import request
from burgerzilla import db, auth_header
from flask_restx import Resource
from burgerzilla.api_models import (Order_Dataset, Order_Menu_Dataset, Order_Menu_ID_Dataset,
                                    New_Order_Dataset, Order_Detail_Dataset, Response_Message)
from burgerzilla.models import User, Menu, Order, Order_Menu
from flask_jwt_extended import jwt_required, get_jwt_identity

from burgerzilla.routes import customer_ns


@customer_ns.route('/order')
class OrderOperations(Resource):
    @jwt_required()
    @customer_ns.doc(body=Order_Detail_Dataset, security="apiKey", params=auth_header,
                  responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials",
                             404: "User Not Found"})
    @customer_ns.response(model=Order_Detail_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=404, description="Not found")
    def get(self):
        user_id = get_jwt_identity()  # JWT den gelmis gibi sayiliyor
        order = Order.query.filter_by(status='NEW', user_id=user_id).first()

        if order == None:
            return {"Message": "There is no valid order!"}, 404

        user = User.query.get(user_id)

        menus = Order_Menu.query.filter_by(order_id=order.id)
        item_list = []
        price = 0

        for menu in menus:
            item = Menu.query.get(menu.menu_id)  # menu item

            price += item.price  # menu price

            item_list.append(item)

        return {"name": user.name, 'address': user.address, 'timestamp': order.timestamp, 'user_id': user_id,
                'restaurant_id': order.restaurant_id, "menus": item_list, "sum_price": price}, 200

    @jwt_required()
    @customer_ns.response(model=New_Order_Dataset, code=201, description="Successful")
    @customer_ns.response(model=Response_Message, code=422, description="Bad request")
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)  # JWT'den geliyor

        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        if order_exists:
            return {"Message": "You already have an active order!"}, 422

        new_order = Order(status="NEW", restaurant_id=user.restaurant_id,
                          user_id=user_id)

        db.session.add(new_order)
        db.session.commit()
        return {"status": new_order.status, "restaurant_id": new_order.restaurant_id, "user_id": new_order.user_id}


@customer_ns.route('/orders')
class ListOrders(Resource):
    @jwt_required()
    @customer_ns.marshal_list_with(Order_Dataset, code=200)
    def get(self):
        user_id = get_jwt_identity()
        # user = User.query.get(user_id) # JWT'den geliyor
        orders = Order.query.filter_by(user_id=user_id)
        ordersList = []

        for order in orders:
            ordersList.append(order)

        return ordersList


@customer_ns.route('/order/add')
class OrderAdd(Resource):
    @jwt_required()
    @customer_ns.marshal_with(Order_Menu_Dataset, code=200, envelope='update_order')
    def post(self):
        user_id = get_jwt_identity()
        menu_id = 1
        user = User.query.get(user_id)  # JWT'den geliyor
        return user.id


@customer_ns.route('/order/delete')
class OrderDelete(Resource):
    @jwt_required()
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        user_id = get_jwt_identity()
        menu_id = 1  # Postmandan verilecek
        menu_id_exists = db.session.query(Menu.id).first() is not None

        if not menu_id_exists:
            return {"Message": "Order could not deleted!"}, 404

        order_id = db.session.query(Order).filter_by(user_id=user_id, status="NEW").first().id

        menu_exists_in_order_menu_table = db.session.query(Order_Menu).filter_by(order_id=order_id,
                                                                                 menu_id=menu_id).first() is not None

        if not menu_exists_in_order_menu_table:
            return {"Message": "Order could not deleted, because there is no valid menu!"}, 404

        del_order = db.session.query(Order_Menu).filter_by(order_id=order_id, menu_id=menu_id).first()
        db.session.delete(del_order)
        db.session.commit()

        return {"Message": "Order successfully deleted!"}, 200


@customer_ns.route('/order/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @customer_ns.marshal_with(Response_Message)
    def post(self):
        user_id = get_jwt_identity()
        order = db.session.query(Order).filter(Order.user_id == user_id,
                                               Order.status == "NEW").first()  # kullancinin siparisi var mi (sepet/order)
        order_exists = order is not None  # kullancinin siparisi var mi (sepet/order)

        if not order_exists:
            return {"Message": "There is no available order!"}, 404

        order_id = order.id

        db.session.query(Order).filter_by(id=order_id).update(
            {'status': 'CANCELLED'})  # Delete degil update olacak burada status icin """Statusu Cancel yap"""
        db.session.commit()

        return {"Message": "Your order has been cancelled!"}, 200


@customer_ns.route('/order/menu')
class OrderMenuOperations(Resource):
    @jwt_required()
    @customer_ns.marshal_list_with(Order_Menu_ID_Dataset, code=200, envelope='order_menu')
    def get(self):
        '''Returns how many menus have been ordered by the user'''
        user_id = get_jwt_identity()
        menus = Order_Menu.query.filter_by(order_id=user_id)
        menu_list = []
        for each in menus:
            menu_list.append(each)

        return menu_list

    @jwt_required()
    @customer_ns.marshal_with(Order_Menu_Dataset, code=201, envelope='order_menu')
    def post(self):
        user_id = get_jwt_identity()
        json_data = request.get_json()
        menu_id = json_data.get('menu_id')

        user_order_id = User.query.filter_by(order_id=user_id).first()

        new_body = Order_Menu(menu_id=menu_id, order_id=user_order_id)
        db.session.add(new_body)
        db.session.commit()
        return new_body
