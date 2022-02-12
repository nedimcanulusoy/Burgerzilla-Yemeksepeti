from flask_restx import Namespace

customer_ns = Namespace("customer", description="Customer Operations")
restaurant_ns = Namespace("restaurant", description="Restaurant Operations")

from burgerzilla.routes import customer, restaurant