from flask_restful import Resource, reqparse, abort
import requests


class RestaurantsByLatLong(Resource):
    def post(self):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the lat of the user")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the lon of the user")
        args = body_parser.parse_args(
            strict=True)  # Accepted only if these two parameters are strictly declared in body else raise exception
        try:
            lat = args['lat']
            lon = args['lon']
            restaurants = requests.get('https://uk.api.just-eat.io/restaurants/bylatlong',
                                       params={'latitude': lat, 'longitude': lon})
            return restaurants.json()
        except Exception as e:
            abort(400, status=400, message="Bad Request", data="")
