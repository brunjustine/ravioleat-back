from flask import request, jsonify, json
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests

from app.services.restaurantService import RESTAURANT

UBER_RESTAURANTS = []

class RestaurantUberCategoryResource(Resource):
    def post(self) -> Dict[str, Any]:
        """
        Return all category restaurants in Uber eat API
        ---
        tags:
            - Flask API
        responses:
            200:
                description: JSON representing all the elements
        """
        body_parser = reqparse.RequestParser(
            bundle_errors=True)  # Throw all the elements that has been filled uncorrectly
        body_parser.add_argument(
            'latitude', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument(
            'longitude', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument(
            'formattedAddress', type=str, required=True, help="Missing the address ")
        args = body_parser.parse_args(strict=True)

        try:  
            latitude = args['latitude']
            longitude = args['longitude']
            formatted_address = args['formattedAddress']  
        except:
            abort(400)
        url = "https://cn-geo1.uber.com/rt/eats/v1/search/home"
        data = {
                    "supportedTypes": ["grid"],
                    "targetLocation": {
                        "address": {
                        "eaterFormattedAddress": formatted_address
                        },
                        "latitude": float(latitude),                                                                                        
                        "longitude": float(longitude)
                }
        }
        headers = {'Content-Type': 'application/json'}
        restaurants = requests.post(url, json=data, headers=headers)
        categories = get_categories(restaurants.json())
        return categories

class RestaurantUberSearchResource(Resource):
    def post(self)-> Dict[str, Any]:
        """
        Return all restaurants in Uber eat API according to a search query
        ---
        tags:
            - Flask API
        responses:
            200:
                description: JSON representing all the elements
        """
        body_parser = reqparse.RequestParser(
            bundle_errors=True)  # Throw all the elements that has been filled uncorrectly
        body_parser.add_argument(
            'latitude', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument(
            'longitude', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument(
            'formattedAddress', type=str, required=True, help="Missing the address ")
        body_parser.add_argument(
            'userQuery', type=str, required=True, help="Missing the user query")
        args = body_parser.parse_args(strict=True)

        try:  
            latitude = args['latitude']
            longitude = args['longitude']
            formatted_address = args['formattedAddress']
            user_query = args['userQuery']  
        except:
            abort(400)
        url = "https://cn-geo1.uber.com/rt/eats/v2/search"
        data = {
            "targetLocation": {
                    "address": {
                    "eaterFormattedAddress": formatted_address
                    },
                    "latitude": float(latitude),
                    "longitude": float(longitude)
                },
                "useRichTextMarkup": True,
                "userQuery": user_query
        }
        headers = {'Content-Type': 'application/json'}
        restaurants = requests.post(url, json=data, headers=headers)
        return restaurants.json()

class RestaurantUberResource(Resource):
    def post(self) -> Dict[str, Any]:
        """
        Return all restaurants in Uber eat API
        ---
        tags:
            - Flask API
        responses:
            200:
                description: JSON representing all the elements
        """
        body_parser = reqparse.RequestParser(
            bundle_errors=True)  # Throw all the elements that has been filled uncorrectly
        body_parser.add_argument(
            'latitude', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument(
            'longitude', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument(
            'formattedAddress', type=str, required=True, help="Missing the address ")
        args = body_parser.parse_args(strict=True)

        try:  
            latitude = args['latitude']
            longitude = args['longitude']
            formatted_address = args['formattedAddress']
            params = {"latitude":float(latitude), "longitude" :float(longitude) , "formatted_address": formatted_address}  
        except:
            abort(400)
        categories = call_category(params)
        #categories = ['pizza']
        del UBER_RESTAURANTS[:]
        UBER_RESTAURANTS.append(get_all_restaurants(params, categories))
        liste_restaurants = initResto()
        return liste_restaurants
        #return UBER_RESTAURANTS

class RestaurantUberByIdResource(Resource):
    def get(self, restaurant_id: str) -> Dict[str,Any]:
        """
        Get the restaurant by his uid
        ---
        tags:
            - Flask API
        parameters:
            - in: path
              name: restaurant_id
              description: The id of the restaurant 
              required: true
              type: string
        responses:
            200:
                description: JSON representing the restaurant
            404:
                description: The restaurant does not exist
        """
        abort_if_restaurant_empty()
        return get_restaurant_by_id(restaurant_id)   
        #return initResto().json()

def call_category(params: Dict[str, Any]):
    url = "http://0.0.0.0:5000/restaurants/uber/categories"
    data = {
            
            "formattedAddress": params['formatted_address'],
            "latitude": params['latitude'],                                                                                        
            "longitude": params['longitude']
    }
    headers = {'Content-Type': 'application/json'}
    categories = requests.post(url, json=data, headers=headers)
    return categories.json()

#get all categories
#def get_categories(categories: Dict[str, Any]):
#    return sum(list(map(lambda grid: list(map(lambda cat : cat['title'], grid['gridItems'])) , categories['suggestedSections'])),[])

#get top categories
def get_categories(categories: Dict[str, Any]):
    top_categories = next((x for x in categories['suggestedSections'] if x['title'] == "Top categories"), None)
    return list(map(lambda category: category['title'] , top_categories['gridItems']))

def get_all_restaurants(params:Dict[str, Any] , categories : Dict[str, Any]):
    categories_regex = ""
    for category in categories:
        categories_regex += category+"|"
    return call_search(params, categories_regex)

def call_search(params : Dict[str, Any], category:str):
    url = "http://0.0.0.0:5000/restaurants/uber/search"
    data = {
            "formattedAddress": params['formatted_address'],
            "latitude": params['latitude'],                                                                                        
            "longitude": params['longitude'],
            "userQuery": category
    }
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, json=data, headers=headers).json()

def abort_if_restaurant_empty():
    if not UBER_RESTAURANTS:
        abort(404,message ='Error : No restaurants found')


def get_restaurant_by_id(restaurant_id : str):
    restaurant_details = UBER_RESTAURANTS[0]['feed']['feedItems']
    map_details = UBER_RESTAURANTS[0]["feed"]["storesMap"]
    return list(filter(lambda e: e['uuid']==restaurant_id, restaurant_details))
    #return map_details

def initResto():
    liste_restaurants = []
    for resto in UBER_RESTAURANTS[0]['feed']['feedItems']:
        restaurant_model = RESTAURANT.copy()
        uuid = resto['uuid']
        attributs = UBER_RESTAURANTS[0]['feed']['storesMap'][uuid]
        restaurant_model.__setitem__("Api","uber_eat")
        restaurant_model.__setitem__("Id",uuid)
        restaurant_model.__setitem__("Name",attributs["title"])
        restaurant_model.__setitem__("UniqueName",None)
        restaurant_model.__setitem__("Address",{
            "City": attributs["location"]["address"]["city"],
            "FirstLine": attributs["location"]["address"]["address1"],
            "Postcode": attributs["location"]["address"]["postalCode"],
            "Latitude": attributs["location"]["latitude"],
            "Longitude": attributs["location"]["longitude"]
        })

        restaurant_model.__setitem__("Rating",{
            "Count": attributs.get("rawRatingStats", {}).get('ratingCount'),
            "StarRating": attributs.get("rawRatingStats", {}).get('storeRatingScore')
        })
       
        restaurant_model.__setitem__("Description", None)
        #todo check if url == url uber_eat+uuid
        restaurant_model.__setitem__("Url",None)
        restaurant_model.__setitem__("LogoUrl",attributs["heroImageUrl"])
        
        available = resto["payload"]["storePayload"]["stateMapDisplayInfo"]["available"]["subtitle"]["text"].split(" min")
        restaurant_model.__setitem__("DeliveryEtaMinutes",{
            "RangeLower": available[0].split("–")[0],
            "RangeUpper": available[0].split("–")[1]
        })
        restaurant_model.__setitem__("IsOpenNow",attributs["isOrderable"])
        restaurant_model.__setitem__("DeliveryCost", attributs.get("fareInfo", {}).get('serviceFee'))
        restaurant_model.__setitem__("Offers",None)
        
        restaurant_model.__setitem__("CuisineTypes", [
            {
            "Id": category["uuid"],
            "Name": category["name"],
            "SeoName": category["keyName"]
            }
            for category in attributs["categories"]
        ] if attributs["categories"] is not None else [])
        restaurant_model.__setitem__("PriceCategory", len(attributs.get("priceBucket","")))
        liste_restaurants.append(restaurant_model)
    return liste_restaurants