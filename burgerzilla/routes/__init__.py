from flask_restx import Namespace

customer_ns = Namespace("customer", description="Customer Operations")
restaurant_ns = Namespace("restaurant", description="Restaurant Operations")
menu_ns = Namespace("menus", description="Menu Operation")

from burgerzilla.routes import customer, restaurant