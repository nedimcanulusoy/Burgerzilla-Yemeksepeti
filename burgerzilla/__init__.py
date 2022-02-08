from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app, doc="/docs", title="Burgerzilla API", description="Burgerzilla Yemeksepeti API", version="1.0")

from burgerzilla.customer import customer
from burgerzilla.restaurant import restaurant
