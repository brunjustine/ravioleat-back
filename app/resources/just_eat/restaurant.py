from flask_restful import abort
import requests
import multiprocessing as mp
from app.resources.just_eat.utils import *

from app.resources.restaurants import get_just_eat_restaurants
from app.services.restaurantWithMenuService import RESTAURANT_WITH_MENU


def get_just_eat_restaurant_by_id(lat, lon, restaurant_id):
    try:

        pool = mp.Pool(mp.cpu_count()*5)

        country_code = get_country_code_from_lat_lon(lat, lon)
        tenant = get_tenant_from_country_code(country_code)

        url = "https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items".format(tenant,
                                                                                       country_code,
                                                                                       restaurant_id)

        restaurant_items = requests.get(url, params={'limit': 1000}).json()
        restaurant_items = remove_bad_items(restaurant_items)
        restaurant_items = [pool.apply_async(add_item_price, args=(country_code,
                                                                   tenant,
                                                                   restaurant_id,
                                                                   restaurant_item))
                            for restaurant_item in restaurant_items]
        restaurant_items = [res.get(timeout=1) for res in restaurant_items]

        pool.close()

        restaurant = get_restaurant_by_id(get_just_eat_restaurants(lat, lon), restaurant_id)
        restaurant = format_json(restaurant, restaurant_items)
        return restaurant

    except Exception as e:
        print(e)
        abort(404)


def get_restaurant_by_id(restaurants, restaurant_id):
    for restaurant in restaurants:
        if int(restaurant['Id']) == int(restaurant_id):
            return restaurant


def remove_bad_items(restaurant_items):
    restaurant_items_tmp = []
    for restaurant_item in restaurant_items['items']:
        if 'description' in restaurant_item.keys():
            restaurant_items_tmp.append(restaurant_item)
    return restaurant_items_tmp


def add_item_price(country_code, tenant, restaurant_id, restaurant_item):
    restaurant_item_id = restaurant_item['id']

    url = "https://{0}.api.just-eat.io/restaurants/{1}/{2}/catalogue/items/{3}/variations" \
        .format(country_code, tenant, restaurant_id, restaurant_item_id)

    item = requests.get(url, params={'limit': 1000}).json()
    item_price = get_item_price(item, restaurant_item_id)
    restaurant_item['price'] = item_price

    return restaurant_item


def get_item_price(item, restaurant_item_id):
    for variation in item['variations']:
        if variation['id'] == restaurant_item_id:
            return variation['basePrice'] / 100


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
                                               } for restaurant_item in restaurant_items
                                           ])
    return restaurant_with_menu_model
