from flask_restx import Resource
from burgerzilla.routes import menu_ns
from burgerzilla.api_models import Menu_Dataset
from burgerzilla.models import Menu


@menu_ns.route('/all')
class MenuOperations(Resource):
    @menu_ns.doc(
        responses={200: "Success", 404: "Menus Not Found"})
    @menu_ns.marshal_list_with(Menu_Dataset, code=200, envelope='menus')
    def get(self):
        """Return all menus of all restaurants"""
        all_menus = Menu.query.all()
        return all_menus
