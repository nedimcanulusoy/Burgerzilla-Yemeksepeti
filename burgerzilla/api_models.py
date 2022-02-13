from flask_restx import fields

from burgerzilla import api
from burgerzilla.order_status import OrderStatus
from burgerzilla.routes import customer_ns, restaurant_ns, auth_ns

Restaurant_Dataset = restaurant_ns.model('Restaurant Name', {
    'name': fields.String()
})

Restaurant_ID_Name_Dataset = restaurant_ns.model('Restaurant', {
    'id': fields.Integer(),
    'name': fields.String()
})

User_Dataset = customer_ns.model('User', {
    'name': fields.String(),
    'surname': fields.String(),
    'username': fields.String(),
    'email': fields.String(),
    'password': fields.String(),
    'address': fields.String(),
    'is_owner': fields.Boolean(default=False),
    'restaurant': fields.Nested(Restaurant_Dataset)
})

Restaurant_ID_Dataset = restaurant_ns.model('Restaurant ID', {
    'restaurant_id': fields.Integer()
})

Menu_Dataset = restaurant_ns.model('Menu', {
    'id': fields.Integer(),
    'name': fields.String(),
    'price': fields.Integer(),
    'description': fields.String(),
    'image': fields.String(),
    'restaurant_id': fields.Integer()
})

Order_Detail_Dataset = customer_ns.model('OrderDetail', {
    "id": fields.Integer(),
    'name': fields.String(),
    'address': fields.String(),
    'status': fields.String(default=OrderStatus.NEW),
    'timestamp': fields.String(),
    'restaurant_id': fields.Integer(),
    'user_id': fields.Integer(),
    'menus': fields.List(fields.Nested(Menu_Dataset)),
    'sum_price': fields.Integer()
})

Order_Dataset = api.model('Order', {
    'id': fields.Integer(),
    'status': fields.String(default=OrderStatus.NEW),
    'timestamp': fields.String(),
    'restaurant_id': fields.Integer(),
    'user_id': fields.Integer(),
})

New_Order_Dataset = customer_ns.model('Order', {
    'status': fields.String(default=OrderStatus.NEW),
    'restaurant_id': fields.Integer(),
    'user_id': fields.Integer()
})

Order_ID_Dataset = customer_ns.model('Order ID', {
    'order_id': fields.Integer()
})

Order_Menu_Dataset = restaurant_ns.model('Order_Menu', {
    'order_id': fields.Integer(),
    'menu_id': fields.Integer()
})

Order_Menu_ID_Dataset = customer_ns.model('Order_Menu_ID', {
    'menu_id': fields.Integer()
})

Update_Order_Status = restaurant_ns.model('Update Order Status', {
    'status': fields.String()
})

Restaurant_Order_Dataset = restaurant_ns.model('Order', {
    'name': fields.String(),
    'address': fields.String(),
    'status': fields.String(),
    'timestamp': fields.String(),
    'restaurant_id': fields.Integer(),
    'user_id': fields.Integer(),
    'menus': fields.List(fields.Nested(Menu_Dataset)),
    'sum_price': fields.Integer()
})

Response_Message = api.model('Message', {
    'Message': fields.String()
})

Error_Dataset = api.model("Error", {
    "result": "error", "message": fields.String()
})

Login_Dataset = auth_ns.model('Login User', {
    'username': fields.String(),
    'password': fields.String()
})

JWT_Dataset = api.model('JWT_Dataset', {
    'Message': fields.String(),
    'access_token': fields.String(),
    'refresh_token': fields.String()
})
