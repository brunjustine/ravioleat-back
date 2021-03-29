from flask_restful import Resource, reqparse, abort
import requests
from app.resources.just_eat.utils import *
from app.resources.restaurants import get_just_eat_restaurants
from app.services.restaurantWithMenuService import RESTAURANT_WITH_MENU


def get_just_eat_restaurant_by_id(lat, lon, restaurant_id):
    try:
        country_code = get_country_code_from_lat_lon(lat, lon)
        tenant = get_tenant_from_country_code(country_code)

        url = "https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items".format(tenant,
                                                                                       country_code,
                                                                                       restaurant_id)

        restaurant_items = requests.get(url, params={'limit': 1000}).json()
        restaurant_items = add_items_prices(country_code, tenant, restaurant_id, restaurant_items)

        restaurant = get_restaurant_by_id(get_just_eat_restaurants(lat, lon), restaurant_id)

        restaurant = format_json(restaurant, restaurant_items)

        return restaurant
    except Exception as e:
        abort(400, status=400, message="Bad Request", data=e.__str__())


def get_restaurant_by_id(restaurants, restaurant_id):
    for restaurant in restaurants:
        if restaurant['Id'] == restaurant_id:
            return restaurant
    abort(404, status=404, message="Not found", data="")


def add_items_prices(country_code, tenant, restaurant_id, restaurants_items):
    for restaurants_item in restaurants_items['items']:
        restaurant_item_id = restaurants_item['id']

        url = "https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items/{3}/variations" \
            .format(country_code, tenant, restaurant_id, restaurant_item_id)
        item = requests.get(url, params={'limit': 1000}).json()
        item_price = get_item_price(item, restaurant_item_id)
        restaurants_item['price'] = item_price

    return restaurants_items


def get_item_price(item, restaurant_item_id):
    for variation in item['variations']:
        if variation['id'] == restaurant_item_id:
            return variation['basePrice'] / 100
    abort(404, status=404, message="Not found", data="")


def format_json(restaurant, restaurant_items):
    restaurant_with_menu_model = RESTAURANT_WITH_MENU.copy()
    restaurant_with_menu_model = {x: restaurant[x] for x in restaurant.keys()}
    restaurant_with_menu_model.__setitem__("Menus",
                                           [
                                               {
                                                   "Id": restaurant_item['id'],
                                                   "Name": restaurant_item['name'],
                                                   "Description": restaurant_item['description'],
                                                   "Price": restaurant_item['price']
                                               } for restaurant_item in restaurant_items['items']
                                           ])
    return restaurant_with_menu_model


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

            restaurant = get_just_eat_restaurant_by_id(lat, lon, restaurant_id)

            # country_code = get_country_code_from_lat_lon(lat, lon)
            # tenant = get_tenant_from_country_code(country_code)
            #
            # url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue'.format(tenant, country_code, restaurant_id)
            # restaurant_headers = requests.get(url, params={'limit': 1000})
            #
            # url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/categories'.format(tenant, country_code, restaurant_id)
            # restaurant_categories = requests.get(url, params={'limit': 1000})
            #
            # url = 'https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items'.format(tenant, country_code, restaurant_id)
            # restaurant_items = requests.get(url, params={'limit': 1000})
            #
            # print(restaurant_headers.json().items())
            # restaurant = merge(merge(restaurant_headers.json(), restaurant_categories.json()), restaurant_items.json())

            return {"status": 200, "message": "OK", "data": restaurant}
        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data="")
