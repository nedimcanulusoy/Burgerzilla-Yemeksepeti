from flask import request
from burgerzilla import api, db
from flask_restx import Resource
from burgerzilla.api_models import (User_Dataset, Order_Dataset, Order_Menu_Dataset, Order_Menu_ID_Dataset,
                                    New_Order_Dataset, Order_Detail_Dataset)
from burgerzilla.models import User, Menu, Order, Order_Menu


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


@api.route('/customer/order')
class OrderOperations(Resource):
    @api.marshal_with(Order_Detail_Dataset)
    def get(self):
        user_id = 1  # JWT den gelmis gibi sayiliyor
        order = Order.query.filter_by(status='NEW', user_id=user_id).first()
        if order == None:
            return {"Error": "There is no valid order!"}, 404
        else:
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

    @api.marshal_with(New_Order_Dataset, envelope='order')
    def post(self):
        user_id = 1
        user = User.query.get(user_id)  # JWT'den geliyor
        order = Order.query.get(user_id)
        status = "NEW"  # statik tanımlanmış durumda

        if order.status == status:
            return {"Error": "You can not create another one until your current order is complete!"}, 404
        else:
            new_order = Order(status=status, restaurant_id=user.restaurant_id,
                              user_id=user_id)

            db.session.add(new_order)
            db.session.commit()
            return new_order, 201  # New order data set


@api.route('/customer/orders')
class ListOrders(Resource):
    @api.marshal_list_with(Order_Dataset, code=200)
    def get(self):
        user_id = 1
        # user = User.query.get(user_id) # JWT'den geliyor
        orders = Order.query.filter_by(user_id=user_id)
        ordersList = []

        for order in orders:
            ordersList.append(order)

        return ordersList


@api.route('/customer/order/add')
class OrderAdd(Resource):
    @api.marshal_with(Order_Menu, code=200, envelope='update_order')
    def post(self):
        user_id = 1
        menu_id = 1
        user = User.query.get(user_id)  # JWT'den geliyor
        return user.id


@api.route('/customer/order/delete')
class OrderDelete(Resource):
    def post(self):
        user_id = 1
        menu_id = 1
        menu_id_exists = db.session.query(Menu.id).first() is not None

        if not menu_id_exists:
            return {"Error": "Order could not deleted!"}, 404

        order_id = db.session.query(Order.id).filter_by(user_id=user_id, status="NEW")
        del_order_menu = db.session.query(Order_Menu.id).filter_by(order_id=order_id, menu_id=menu_id)
        db.session.delete(del_order_menu)
        db.session.commit()

        return {"Message": "DELETED!"}, 200


@api.route('/customer/order/<int:id>')
class OrderMenuOperations(Resource):
    @api.marshal_list_with(Order_Menu_ID_Dataset, code=200, envelope='order_menu')
    def get(self, id):
        '''Returns how many menus have been ordered by the user'''
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
