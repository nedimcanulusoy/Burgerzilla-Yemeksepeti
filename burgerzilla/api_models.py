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

Menu_Dataset = api.model('Menu', {'product': fields.String(),
                                  'price': fields.String(),
                                  'description': fields.String(),
                                  'image': fields.String(),
                                  'restaurant_id': fields.Integer()})

Order_Dataset = api.model('Order', {'name': fields.String(),
                                    'price': fields.Integer(),
                                    'quantity': fields.Integer(),
                                    'status': fields.String(),
                                    'timestamp': fields.String(),
                                    'restaurant_id': fields.Integer(),
                                    'user_id': fields.Integer()
                                    })

Order_Menu_Dataset = api.model('Order_Menu', {'order_id': fields.Integer(),
                                              'menu_id': fields.Integer()})

Order_Menu_ID_Dataset = api.model('Order_Menu', {'menu_id': fields.Integer()})
