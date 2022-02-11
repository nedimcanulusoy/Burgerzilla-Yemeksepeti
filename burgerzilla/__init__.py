from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from flask_user import UserManager

from burgerzilla.config import Config
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
api = Api()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from .models import User
    user_manager = UserManager(app, db, User)

    from burgerzilla.routes.auth import auth
    from burgerzilla.routes.customer import customer
    from burgerzilla.routes.restaurant import restaurant

    api.add_namespace(auth)
    api.add_namespace(customer)
    api.add_namespace(restaurant)
    api.init_app(app, title="Burgerzilla API", description="Burgerzilla Yemeksepeti API", version="1.0")


    return app
