from flask_restx import fields
from burgerzilla import api

Customer_Dataset = api.model('Customer', {'customer_name': fields.String(),
                                          'customer_surname': fields.String(),
                                          'customer_username': fields.String(),
                                          'customer_email': fields.String(),
                                          'customer_password': fields.String(),
                                          'customer_address': fields.String()})

Owner_Dataset = api.model('Owner', {'owner_name': fields.String(),
                                    'owner_surname': fields.String(),
                                    'owner_username': fields.String(),
                                    'owner_email': fields.String(),
                                    'owner_password': fields.String(),
                                    'owner_address': fields.String()})

Restaurant_Dataset = api.model('Restaurant', {'restaurant_name': fields.String()})

Menu_Dataset = api.model('Menu', {'product': fields.String(),
                                  'price': fields.String(),
                                  'description': fields.String(),
                                  'image': fields.String()})

Order_Dataset = api.model('Order', {'order_name': fields.String(),
                                    'order_price': fields.Integer(),
                                    'order_quantity': fields.Integer(),
                                    'order_accept_cancel': fields.Integer(),
                                    'order_status': fields.String(),
                                    'order_timestamp': fields.String()})
