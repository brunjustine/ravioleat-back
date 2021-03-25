from flask_restful import Resource, reqparse, abort
import requests
from app.resources.just_eat.utils import *


class RestaurantsByLatLong(Resource):
    def post(self):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the lat of the user")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the lon of the user")
        # Accepted only if these two parameters are strictly declared in body else raise exception
        args = body_parser.parse_args(strict=True)

        try:
            lat = args['lat']
            lon = args['lon']

            country_code = get_country_code_from_lat_lon(lat, lon)
            tenant = get_tenant_from_country_code(country_code)

            url = 'https://{0}.api.just-eat.io/restaurants/bylatlong'.format(tenant)

            restaurants = requests.get(url,
                                       params={'latitude': float(lat), 'longitude': float(lon)},
                                       headers={'Accept-Tenant': country_code})

            return {"status": 200, "message": "OK", "data": restaurants.json()}
        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data="")