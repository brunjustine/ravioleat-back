from flask_restful import abort
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

        restaurants = format_json(restaurants.json(), country_code)

        return restaurants
    except Exception as e:
        print(e.__str__())
        return {}


def get_just_eat_restaurant_search(lat, lon, search_term):

    try:
        country_code = get_country_code_from_lat_lon(lat, lon)
        tenant = get_tenant_from_country_code(country_code)

        url = 'https://{0}.api.just-eat.io/search/restaurants/{1}'.format(tenant, country_code)
        restaurants = requests.get(url,
                                   params={'searchTerm': search_term, 'latlong': lat + ',' + lon},
                                   headers={'Accept-Tenant': country_code})

        restaurants_ids = get_restaurants_ids(restaurants.json())
        restaurants = get_restaurants_by_ids(restaurants_ids, get_just_eat_restaurants(lat, lon))

        return restaurants
    except Exception as e:
        print(e.__str__())
        return {}


def get_restaurants_ids(restaurants):
    ids = []
    for restaurant in restaurants['restaurants']:
        ids.append(int(restaurant['restaurantId']))
    return ids


def get_restaurants_by_ids(ids, all_restaurants):
    restaurants = []
    for restaurant in all_restaurants:
        if restaurant['Id'] in ids:
            restaurants.append(restaurant)
    return restaurants


def format_json(restaurants, country_code):
    restaurant_list = []

    for restaurant in restaurants["Restaurants"]:
        restaurant_model = RESTAURANT.copy()

        restaurant_model.__setitem__('Api', 'just_eat')
        restaurant_model.__setitem__('Id', restaurant['Id'])
        restaurant_model.__setitem__('Name', restaurant['Name'])
        restaurant_model.__setitem__('UniqueName', restaurant['UniqueName'].replace("-"," "))
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
                                         "StarRating": resize_star_rating(
                                             restaurant['Rating']['StarRating'], country_code
                                         )
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


def resize_star_rating(star_rating, country_code):
    return (5 * star_rating) / 6 if country_code == 'uk' else star_rating


