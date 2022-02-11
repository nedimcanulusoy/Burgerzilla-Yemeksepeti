from flask_restx import Namespace

auth = Namespace("auth", description="Auth Operations")

from burgerzilla.routes.auth import login, register
