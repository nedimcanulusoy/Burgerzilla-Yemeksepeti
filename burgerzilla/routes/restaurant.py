from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from burgerzilla import db, auth_header
from flask_restx import Resource, marshal
from burgerzilla.api_models import (Restaurant_Dataset, Menu_Dataset, Order_Menu_Dataset,
                                    Restaurant_Order_Dataset, Response_Message)
from burgerzilla.models import User, Restaurant, Menu, Order, Order_Menu

from burgerzilla.routes import restaurant_ns
from burgerzilla.routes.utils import owner_required


@restaurant_ns.route('/')
@restaurant_ns.doc(
    responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials", 404: "User Not Found"})
class RestaurantOperations(Resource):
    @restaurant_ns.marshal_list_with(Restaurant_Dataset, code=200, envelope='restaurants')
    def get(self):
        """Returns all restaurants"""
        try:
            all_restaurants = Restaurant.query.all()
            restaurant_ns.logger.debug('GET request was `successful` at RestaurantOperations')
            return all_restaurants

        except Exception as e:
            restaurant_ns.logger.debug('GET request was `unsuccessful` at RestaurantOperations')
            return {"Message": f"An error occurred! {e}"}

@restaurant_ns.route('/menu')
class MenuOperations(Resource):
    # @restaurant_ns.doc(
    #     responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials", 404: "User Not Found"})
    # @restaurant_ns.marshal_list_with(Menu_Dataset, code=200, envelope='menus')
    # def get(self):
    #     all_menus = Menu.query.all()
    #     return all_menus

    @jwt_required()
    @restaurant_ns.doc(body=Menu_Dataset, params=auth_header,
                       responses={200: "Success", 400: "Validation Error", 403: "Invalid Credentials",
                                  404: "User Not Found"})
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

        try:
            new_menu = Menu(name=name, price=price, description=description, image=image, restaurant_id=restaurant_id)
            db.session.add(new_menu)
            db.session.commit()
            restaurant_ns.logger.debug('POST request was `successful` at MenuOperations')
            return new_menu

        except Exception as e:
            restaurant_ns.logger.debug('POST request was `unsuccessful` at MenuOperations')
            return {"Message": f"An error occurred! {e}"}


@restaurant_ns.route('/<int:id>/menu')
class GetRestaurantMenu(Resource):
    @restaurant_ns.doc(
        responses={201: "Success", 400: "Validation Error", 403: "Invalid Credentials", 404: "User Not Found"})
    @restaurant_ns.marshal_list_with(Menu_Dataset, code=201, envelope='menus')
    def get(self, id):
        """Returns the menu according to the ID of the restaurant"""
        try:
            restaurant_menus = Menu.query.filter_by(restaurant_id=id).all()
            restaurant_ns.logger.debug('GET request was `successful` at GetRestaurantMenu')
            return restaurant_menus, 201

        except Exception as e:
            restaurant_ns.logger.debug('GET request was `unsuccessful` at GetRestaurantMenu')
            return {"Message": f"An error occurred! {e}"}

@restaurant_ns.route('/order')
class RestaurantOrder(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header)
    @restaurant_ns.marshal_list_with(Order_Menu_Dataset, envelope='restaurant_order_item')
    def get(self):
        '''Returns which menu order was taken'''
        user_id = get_jwt_identity()

        try:
            user = User.query.get(user_id)
            order = Order.query.filter_by(user_id=user.id).first()
            menus = Order_Menu.query.filter_by(order_id=order.id)

            item_list = []
            for each in menus:
                item_list.append(each)

            restaurant_ns.logger.debug('GET request was `successful` at RestaurantOrder')
            return item_list

        except Exception as e:
            restaurant_ns.logger.debug('GET request was `unsuccessful` at RestaurantOrder')
            return {"Message": f"An error occurred! {e}"}

@restaurant_ns.route('/order/detail')
class RestaurantOrderDetail(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header)
    @restaurant_ns.response(model=Restaurant_Order_Dataset, code=201, description='restaurant_order_item_detail')
    def get(self):
        '''Returns order details of the user to the Restaurant'''
        user_id = get_jwt_identity()  # JWT den gelmis gibi sayiliyor
        order = Order.query.filter_by(status='NEW', user_id=user_id).first()

        try:
            if order is None:
                restaurant_ns.logger.info('No valid order: at RestaurantOrderDetail')
                return {"Error": "Your restaurant does not have any pending orders at the moment!"}, 404

            order_status = Order.query.filter_by(status='NEW', user_id=user_id).update({'status': 'PENDING'})
            db.session.commit()

            user = User.query.get(user_id)

            menus = Order_Menu.query.filter_by(order_id=order.id)
            item_list = []
            price = 0

            for menu in menus:
                item = Menu.query.get(menu.menu_id)  # menu item
                price += item.price  # menu price
                item_list.append(item)

            restaurant_ns.logger.debug('GET request was `successful` at RestaurantOrderDetail')
            return marshal(
                {"name": user.name, 'address': user.address, 'timestamp': order.timestamp, 'user_id': user_id,
                 'status': order_status,
                 'restaurant_id': order.restaurant_id, "menus": item_list, "sum_price": price},
                Restaurant_Order_Dataset), 201

        except Exception as e:
            restaurant_ns.logger.debug('GET request was `unsuccessful` at RestaurantOrderDetail')
            return {"Message": f"An error occurred! {e}"}

@restaurant_ns.route('/order/cancel')
class OrderCancel(Resource):
    @jwt_required()
    @owner_required()
    @restaurant_ns.doc(params=auth_header)
    @restaurant_ns.marshal_with(Response_Message)
    def post(self):
        """Cancel user's order by restaurant"""
        order_id = get_jwt_identity()  # postmandan gelecek
        order_id_exists = db.session.query(Order).filter(Order.id == order_id, Order.status != "NEW",
                                                         Order.status != "CANCELLED").first() is not None  # kullancinin siparisi var mi (sepet/order)

        try:
            if not order_id_exists:
                restaurant_ns.logger.info('No valid order: at OrderCancel')
                return {"Message": "There is no available order!"}, 404

            db.session.query(Order).filter_by(id=order_id).update(
                {'status': 'CANCELLED'})  # Delete degil update olacak burada status icin """Statusu Cancel yap"""
            db.session.commit()

            restaurant_ns.logger.debug('POST request was `successful` at OrderCancel')
            return {"Message": "DELETED!"}, 200


        except Exception as e:
            restaurant_ns.logger.debug('POST request was `unsuccessful` at OrderCancel')
            return {"Message": f"An error occurred! {e}"}