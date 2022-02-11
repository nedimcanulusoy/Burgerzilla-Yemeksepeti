from flask_restx import Namespace

restaurant = Namespace("restaurant", description='Restaurant Operations')

from burgerzilla.routes.restaurant import restaurant