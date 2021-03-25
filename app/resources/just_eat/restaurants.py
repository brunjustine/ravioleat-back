from flask_restful import Resource, reqparse, abort
import requests
from app.resources.just_eat.utils import *
from app.services.restaurantService import RESTAURANT
from flask import jsonify


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

            restaurants = format_json(restaurants.json())
            #print(restaurants)

            return {"status": 200, "message": "OK", "data": restaurants}
        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data="")


def format_json(restaurants):
    restaurant_list = []
    for restaurant in restaurants["Restaurants"]:
        #print([x for x in restaurant['CuisineTypes']])
        restaurant_model = RESTAURANT

        restaurant_model.__setitem__('Id', restaurant['Id'])
        restaurant_model.__setitem__('Name', restaurant['Name'])
        restaurant_model.__setitem__('UniqueName', restaurant['UniqueName'])
        restaurant_model.__setitem__('Address',
                                     {
                                         "City": restaurant['Address']['City'],
                                         "FirstLine": restaurant['Address']['FirstLine'],
                                         "Postcode": restaurant['Address']['Postcode'],
                                         "Latitude": restaurant['Address']['Latitude'],
                                         "Longitude": restaurant['Address']['Longitude']
                                     })
        restaurant_model.__setitem__('Rating',
                                     {
                                         "Count": restaurant['Rating']['Count'],
                                         "StarRating": restaurant['Rating']['StarRating']
                                     })
        restaurant_model.__setitem__('Description', restaurant['Description'])
        restaurant_model.__setitem__('Url', restaurant['Url'])
        restaurant_model.__setitem__('LogoUrl', restaurant['LogoUrl'])
        if restaurant['DeliveryEtaMinutes'] is not None:
            restaurant_model.__setitem__('DeliveryEtaMinutes',
                                         {
                                             'RangeLower': restaurant['DeliveryEtaMinutes']['RangeLower'],
                                             'RangeUpper': restaurant['DeliveryEtaMinutes']['RangeUpper']
                                         })
        restaurant_model.__setitem__('DeliveryEtaMinutes', None)
        restaurant_model.__setitem__('IsOpenNow', restaurant['IsOpenNow'])
        restaurant_model.__setitem__('DeliveryCost', restaurant['DeliveryCost'])
        restaurant_model.__setitem__('Offers',
                                     [
                                         {
                                             'Type': offer['Type'],
                                             'Amount': offer['Amount'],
                                             'Description': offer['Description'],
                                             'OfferId': offer['OfferId']
                                         }
                                         for offer in restaurant['Offers']
                                     ])
        restaurant_model.__setitem__('CuisineTypes',
                                     [
                                         {
                                             'Id': cuisine_type['Id'],
                                             'Name': cuisine_type['Name'],
                                             'SeoName': cuisine_type['SeoName']
                                         }
                                         for cuisine_type in restaurant['CuisineTypes']
                                     ])

        restaurant_model.__setitem__('OpeningTimes',
                                     {
                                         'Open': '',
                                         'Close': ''
                                     })
        restaurant_model.__setitem__('PriceCategory', None)
        restaurant_list.append(restaurant_model)
    return restaurant_list
