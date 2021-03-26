from flask_restful import Resource, reqparse, abort
import requests
from jsonmerge import merge
from app.resources.just_eat.utils import *


class RestaurantByID(Resource):
    def post(self, restaurant_id):
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

            url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue'.format(tenant, country_code, restaurant_id)
            restaurant_headers = requests.get(url, params={'limit': 1000})

            url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/categories'.format(tenant, country_code, restaurant_id)
            restaurant_categories = requests.get(url, params={'limit': 1000})

            url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items'.format(tenant, country_code, restaurant_id)
            restaurant_items = requests.get(url, params={'limit': 1000})

            print(restaurant_headers.json().items())
            restaurant = merge(merge(restaurant_headers.json(), restaurant_categories.json()), restaurant_items.json())

            return {"status": 200, "message": "OK", "data": restaurant}
        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data="")