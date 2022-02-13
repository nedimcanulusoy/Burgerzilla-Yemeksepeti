from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate

from burgerzilla.config import Config
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

import logging

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
api = Api()

auth_header = {
    'Authorization': {'in': 'header', 'description': "An authorization token: 'Bearer \<token\>'", 'required': True}}


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    logging.basicConfig(filename='burgerzilla.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from burgerzilla.routes import auth_ns, customer_ns, restaurant_ns, menu_ns

    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
    }
    api.init_app(app, doc=True, title="Burgerzilla API", description="Burgerzilla Yemeksepeti API", version="1.0",
                 security='Bearer Auth', authorizations=authorizations)

    api.add_namespace(auth_ns)
    api.add_namespace(customer_ns)
    api.add_namespace(restaurant_ns)
    api.add_namespace(menu_ns)

    return app
