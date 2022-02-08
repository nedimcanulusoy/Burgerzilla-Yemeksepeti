from flask_restx import fields
from burgerzilla import api

User_Dataset = api.model('User', {'name': fields.String(),
                                  'surname': fields.String(),
                                  'username': fields.String(),
                                  'email': fields.String(),
                                  'password': fields.String(),
                                  'address': fields.String(),
                                  'restaurant_id': fields.Integer(default=-1)})

Restaurant_Dataset = api.model('Restaurant', {'name': fields.String()})

Menu_Dataset = api.model('Menu', {'name': fields.String(),
                                  'price': fields.Integer(),
                                  'description': fields.String(),
                                  'image': fields.String(),
                                  'restaurant_id': fields.Integer()})

Order_Detail_Dataset = api.model('OrderDetail', {'name': fields.String(),
                                                 'address': fields.String(),
                                                 'status': fields.String(default='NEW'),
                                                 'timestamp': fields.String(),
                                                 'restaurant_id': fields.Integer(),
                                                 'user_id': fields.Integer(),
                                                 'menus': fields.List(fields.Nested(Menu_Dataset)),
                                                 'sum_price': fields.Integer()
                                                 })

Order_Dataset = api.model('Order', {'id': fields.Integer(),
                                    'status': fields.String(default='NEW'),
                                    'timestamp': fields.String(),
                                    'restaurant_id': fields.Integer(),
                                    'user_id': fields.Integer(),
                                    })

# New order data set
New_Order_Dataset = api.model('Order', {'status': fields.String(default='NEW'),
                                        'restaurant_id': fields.Integer(),
                                        'user_id': fields.Integer()})

Order_Menu_Dataset = api.model('Order_Menu', {'order_id': fields.Integer(),
                                              'menu_id': fields.Integer()})

Order_Menu_ID_Dataset = api.model('Order_Menu', {'menu_id': fields.Integer()})

Restaurant_Order_Dataset = api.model('Order', {'name': fields.String(),
                                               'address': fields.String(),
                                               'status': fields.String(),
                                               'timestamp': fields.String(),
                                               'restaurant_id': fields.Integer(),
                                               'user_id': fields.Integer(),
                                               'menus': fields.List(fields.Nested(Menu_Dataset)),
                                               'sum_price': fields.Integer()
                                               })

Delete_Msg = {'Message': fields.String(default="Order has been successfully deleted!")}

Error_Dataset = api.model("Error", {"result": "error", "message": fields.String})
