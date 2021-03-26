from flask import request, jsonify, json
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests

RESTAURANTS = []

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
        RESTAURANTS = get_all_restaurants(params, categories)
        return RESTAURANTS

    

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


def get_categories(categories: Dict[str, Any]):
    top_categories = next((x for x in categories['suggestedSections'] if x['title'] == "Top categories"), None)
    return list(map(lambda category: category['title'] , top_categories['gridItems']))

#def get_all_restaurants(params:Dict[str, Any] , categories : Dict[str, Any]):
#    restaurants=[]
#    for category in categories:
#        restaurants.append(call_search(params,category))
#    return restaurants

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