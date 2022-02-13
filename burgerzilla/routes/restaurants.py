from flask_restx import Resource

from burgerzilla.api_models import Restaurant_ID_Name_Dataset
from burgerzilla.models import Restaurant
from burgerzilla.routes import restaurants_ns


@restaurants_ns.route('')
@restaurants_ns.doc(
    responses={200: "Success", 404: "Not Found"})
class RestaurantOperations(Resource):
    @restaurants_ns.marshal_list_with(Restaurant_ID_Name_Dataset, code=200, envelope='restaurants')
    def get(self):
        """Returns all restaurants"""
        all_restaurants = Restaurant.query.all()
        restaurants_ns.logger.debug('GET request was `successful` at RestaurantOperations')
        return all_restaurants
