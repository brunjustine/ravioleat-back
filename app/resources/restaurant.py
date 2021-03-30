from flask_restful import Resource, reqparse, abort
from app.resources.just_eat.restaurant import get_just_eat_restaurant_by_id
from app.resources.deliveroo.restaurant import get_deliveroo_restaurant_by_id
from app.resources.uber_eat.restaurant import get_uber_eat_restaurant_by_id


class RestaurantById(Resource):
    def post(self, restaurant_id):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument('api', type=str, required=True, help="Missing the API")
        body_parser.add_argument('userQuery', type=str, required=True, help="Missing the user query ")
        body_parser.add_argument('formattedAddress', type=str, required=True, help="Missing the address ")
        args = body_parser.parse_args(strict=True)

        # Accepted only if these two parameters are strictly declared in body else raise exception
        args = body_parser.parse_args(strict=True)

        try:
            lat = args['lat']
            lon = args['lon']
            api = args['api']
            user_query = args['userQuery']
            formatted_address = args['formattedAddress']

            if api == "just_eat" :
                restaurant = get_just_eat_restaurant_by_id(lat, lon, restaurant_id)
            elif api == "deliveroo":
                restaurant = get_deliveroo_restaurant_by_id(lat, lon, restaurant_id)
            elif api == "uber_eat":
                restaurant = get_uber_eat_restaurant_by_id(lat, lon, formatted_address, user_query, restaurant_id)
            else :
                abort(404, status=404, message="Not found", data="API not found")
            return {"status": 200, "message": "OK", "data": restaurant}
        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data=e.__str__())