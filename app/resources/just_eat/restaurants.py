from flask_restful import Resource, reqparse, abort
import requests
from app.resources.just_eat.utils import *
from app.services.restaurantService import RESTAURANT


def get_just_eat_restaurants(lat, lon):

    try:
        country_code = get_country_code_from_lat_lon(lat, lon)
        tenant = get_tenant_from_country_code(country_code)

        url = 'https://{0}.api.just-eat.io/restaurants/bylatlong'.format(tenant)

        restaurants = requests.get(url,
                                   params={'latitude': float(lat), 'longitude': float(lon)},
                                   headers={'Accept-Tenant': country_code})

        restaurants = format_json(restaurants.json())

        return restaurants
    except Exception as e:
        print(e)
        abort(400, status=400, message="Bad Request", data=e.__str__())

# class RestaurantsByLatLongSearch(Resource):
#     def post(self):
#         body_parser = reqparse.RequestParser()
#         body_parser.add_argument('lat', type=str, required=True, help="Missing the latitude")
#         body_parser.add_argument('lon', type=str, required=True, help="Missing the longitude")
#         body_parser.add_argument('searchTerm', type=str, required=True, help="Missing the searchTerm")
#         # Accepted only if these two parameters are strictly declared in body else raise exception
#         args = body_parser.parse_args(strict=True)
#
#         try:
#             lat = args['lat']
#             lon = args['lon']
#             search_term = args['searchTerm']
#
#             country_code = get_country_code_from_lat_lon(lat, lon)
#             tenant = get_tenant_from_country_code(country_code)
#
#             url = 'https://{0}.api.just-eat.io/search/restaurants/{1}'.format(tenant, country_code)
#
#             restaurants = requests.get(url,
#                                        params={'searchTerm': search_term, 'latlong': lat + ',' + lon},
#                                        headers={'Accept-Tenant': country_code})
#
#             restaurants_ids = get_restaurants_ids(restaurants.json())
#             restaurants = get_restaurants_by_ids(restaurants_ids, RESTAURANTS)
#
#             return {"status": 200, "message": "OK", "data": restaurants}
#         except Exception as e:
#             print(e)
#             abort(400, status=400, message="Bad Request", data=e.__str__())
#
#
# def get_restaurants_ids(restaurants):
#     ids = []
#     for restaurant in restaurants['restaurants']:
#         ids.append(restaurant['restaurantId'])
#     return ids
#
#
# def get_restaurants_by_ids(ids, restaurants):
#     restaurants_tmp = []
#     for restaurant in restaurants:
#         print(restaurant)
#         if restaurant['Id'] in ids:
#             restaurants_tmp.append(restaurant)
#     return restaurants_tmp


def format_json(restaurants):
    restaurant_list = []

    for restaurant in restaurants["Restaurants"]:
        restaurant_model = RESTAURANT.copy()

        restaurant_model.__setitem__('Api', 'just-eat')
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
        else:
            restaurant_model.__setitem__('DeliveryEtaMinutes', None)
        restaurant_model.__setitem__('IsOpenNow', restaurant['IsOpenNow'])
        restaurant_model.__setitem__('DeliveryCost', restaurant['DeliveryCost'])
        restaurant_model.__setitem__('Offers',
                                     [
                                         {
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
        restaurant_model.__setitem__('PriceCategory', None)
        restaurant_list.append(restaurant_model)
    return restaurant_list

