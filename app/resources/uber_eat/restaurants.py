from flask import request, jsonify, json
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests

from app.services.restaurantService import RESTAURANT

UBER_RESTAURANTS = []

def call_category(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return all category restaurants in Uber eat API
    ---
    tags:
        - Flask API
    responses:
        200:
            description: JSON representing all the elements
    """
    url = "https://cn-geo1.uber.com/rt/eats/v1/search/home"
    data = {
                "supportedTypes": ["grid"],
                "targetLocation": {
                    "address": {
                    "eaterFormattedAddress": params['formatted_address']
                    },
                    "latitude": float(params['latitude']),                                                                                        
                    "longitude": float(params['longitude'])
            }
    }
    headers = {'Content-Type': 'application/json'}
    restaurants = requests.post(url, json=data, headers=headers)
    categories = get_categories(restaurants.json())
    return categories

def call_search(params : Dict[str, Any])-> Dict[str, Any]:
    """
    Return all restaurants in Uber eat API according to a search query
    ---
    tags:
        - Flask API
    responses:
        200:
            description: JSON representing all the elements
    """
    url = "https://cn-geo1.uber.com/rt/eats/v2/search"
    data = {
        "targetLocation": {
                "address": {
                "eaterFormattedAddress": params['formatted_address']
                },
                "latitude": float(params['latitude']),
                "longitude": float(params['longitude'])
            },
            "useRichTextMarkup": True,
            "userQuery": params['user_query']
    }
    headers = {'Content-Type': 'application/json'}
    restaurants = requests.post(url, json=data, headers=headers)
    return restaurants.json()

def get_uber_eat_restaurants(latitude, longitude, formatted_address, user_query) -> Dict[str, Any]:
    """
    Return all restaurants in Uber eat API
    ---
    tags:
        - Flask API
    responses:
        200:
            description: JSON representing all the elements
    """

    try:  
        params = {"latitude":float(latitude), "longitude" :float(longitude) , "formatted_address": formatted_address}  
        params['user_query'] = user_query if user_query != "" else get_formatted_categories(params)
    except:
        abort(400)
    del UBER_RESTAURANTS[:]
    UBER_RESTAURANTS.append(call_search(params))
    liste_restaurants = initResto()
    return liste_restaurants

#get all categories
#def get_categories(categories: Dict[str, Any]):
#    return sum(list(map(lambda grid: list(map(lambda cat : cat['title'], grid['gridItems'])) , categories['suggestedSections'])),[])

#get top categories
def get_categories(categories: Dict[str, Any]):
    top_categories = next((x for x in categories['suggestedSections'] if x['title'] == "Top categories"), None)
    return list(map(lambda category: category['title'] , top_categories['gridItems']))

def get_formatted_categories(params: Dict[str, Any]):
    categories = call_category(params)
    categories_regex = ""
    for category in categories:
        categories_regex += category+"|"
    return categories_regex

def initResto():
    liste_restaurants = []
    for resto in UBER_RESTAURANTS[0]['feed']['feedItems']:
        if resto['type'] == 'STORE':
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
            restaurant_model.__setitem__("LogoUrl",attributs.get("heroImageUrl",""))
            
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

    