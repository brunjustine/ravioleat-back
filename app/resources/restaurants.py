from flask_restful import Resource, reqparse, abort
from app.resources.just_eat.restaurants import get_just_eat_restaurants
from app.resources.deliveroo.restaurants import get_deliveroo_restaurants
from app.resources.uber_eat.restaurants import get_uber_eat_restaurants


class RestaurantsByLatLong(Resource):
    def post(self):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument('formattedAddress', type=str, required=True, help="Missing the address ")
        body_parser.add_argument('userQuery', type=str, required=True, help="Missing the user query ")
        args = body_parser.parse_args(strict=True)

        # Accepted only if these two parameters are strictly declared in body else raise exception
        args = body_parser.parse_args(strict=True)

        try:
            lat = args['lat']
            lon = args['lon']
            formatted_address = args['formattedAddress']
            user_query = args['userQuery']

            restaurants = []

            restaurants.extend(get_just_eat_restaurants(lat, lon))
            restaurants.extend(get_deliveroo_restaurants(lat, lon))
            restaurants.extend(get_uber_eat_restaurants(lat, lon, formatted_address, user_query))

            return restaurants

        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data=e.__str__())