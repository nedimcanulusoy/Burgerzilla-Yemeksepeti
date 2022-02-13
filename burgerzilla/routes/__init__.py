from flask_restx import Namespace

auth_ns = Namespace("auth", description="Auth Operations")
customer_ns = Namespace("customer", description="Customer Operations")
restaurant_ns = Namespace("restaurant", description="Restaurant Operations")
menu_ns = Namespace("menus", description="Getting all menus from any restaurant")
restaurants_ns = Namespace("restaurants", description="Getting all restaurants")

from burgerzilla.routes import customer, restaurant, auth, menus, restaurants
