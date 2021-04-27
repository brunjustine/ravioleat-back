from flask import request, jsonify, json
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests

from app.services.restaurantService import RESTAURANT
from app.resources.uber_eat.categories import *

UBER_RESTAURANTS = []

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
        params['user_query'] = user_query if user_query != "" else get_formatted_categories(params)[0:100]
    except:
        abort(400)

    liste_restaurants = []
    if params['user_query'] is not None :
        del UBER_RESTAURANTS[:]
        UBER_RESTAURANTS.append(call_search(params))
        liste_restaurants = init_resto() 
    return liste_restaurants

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

def init_resto():
    liste_restaurants = []
    if ('feed' in UBER_RESTAURANTS[0] and UBER_RESTAURANTS[0]['feed']['feedItems'] is not None):
        for resto in UBER_RESTAURANTS[0]['feed']['feedItems']:
            if resto['type'] == 'STORE':
                restaurant_model = RESTAURANT.copy()
                uuid = resto['uuid']
                
                attributs = UBER_RESTAURANTS[0]['feed']['storesMap'][uuid]
                restaurant_model.__setitem__("Api","uber_eat")
                restaurant_model.__setitem__("Id",uuid)
                restaurant_model.__setitem__("Name",attributs.get("title",None))
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

                
                try : 
                    available = resto["payload"]["storePayload"]["stateMapDisplayInfo"]["available"]["subtitle"]["text"].split(" min")
                    restaurant_model.__setitem__("DeliveryEtaMinutes",{
                        "RangeLower": available[0].split("–")[0],
                        "RangeUpper": available[0].split("–")[1]
                    })
                except : 
                    restaurant_model.__setitem__("DeliveryEtaMinutes",None)
            
                restaurant_model.__setitem__("IsOpenNow",attributs.get("isOrderable",None))
                restaurant_model.__setitem__("DeliveryCost", attributs.get("fareInfo", {}).get('serviceFee'))
                restaurant_model.__setitem__("Offers",[])
                
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

