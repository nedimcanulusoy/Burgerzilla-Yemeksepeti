from flask_restx import Namespace

customer = Namespace("customer", description='Customer Operations')

from burgerzilla.routes.customer import customer