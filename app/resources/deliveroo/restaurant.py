from flask import request
from flask_restful import Resource, reqparse, abort

from typing import Dict, List, Any

import requests

from app.services.restaurantWithMenuService import RESTAURANT_WITH_MENU
from app.resources.deliveroo.restaurants import get_deliveroo_restaurants, search



def get_deliveroo_restaurant_by_id(lat, lng, id_restaurant):
    headers = {"X-Roo-Country":"fr", "Accept-Language":"fr-fr", "User":"Deliveroo-OrderApp/3.73.0","Content-Type":"application/json"}
    try :
        url = "https://api.fr.deliveroo.com/orderapp/v1/restaurants/"+str(id_restaurant)
        response_dict = requests.get(url,headers=headers).json()
        res = initRestoById(lat,lng,response_dict)
        return({"status":200,"message":"OK","data":res})
    except Exception as e:
                print(e)
                abort(400, status=400, message="Bad Request", data=e.__str__())
        
def initRestoById(lat,lng,restaurant_by_id):
    liste_restaurants = get_deliveroo_restaurants(lat,lng)
    restaurant = get_resto_by_id(liste_restaurants,restaurant_by_id['id'])
    restaurant_with_menu_model = RESTAURANT_WITH_MENU.copy()
    restaurant_with_menu_model = {x: restaurant[x] for x in restaurant.keys()}
    restaurant_with_menu_model.__setitem__("UniqueName",restaurant_by_id['uname'])
    restaurant_with_menu_model.__setitem__("Address",{
        "City": restaurant_by_id["address"]["city"],
        "Firstline": restaurant_by_id["address"]["address1"],
        "Postcode": restaurant_by_id["address"]["post_code"],
        "Latitude": restaurant_by_id["address"]["coordinates"][0],
        "Longitude": restaurant_by_id["address"]["coordinates"][1]
    })
    restaurant_with_menu_model.__setitem__("Rating",{
        "Count": restaurant_by_id["rating"]["value"],
        "StarRating": restaurant_by_id["rating"]["formatted_count"]
    })
    restaurant_with_menu_model.__setitem__("Description", restaurant_by_id["description"])
    restaurant_with_menu_model.__setitem__("Url", restaurant_by_id["share_url"])
    restaurant_with_menu_model.__setitem__("IsOpenNow", restaurant_by_id["open"])
    restaurant_with_menu_model.__setitem__("Menus",[
        {
            'Id': menu['id'],
            'Name': menu['name'],
            'Description': menu['description'],
            'Price': menu['price']
        }
        for menu in restaurant_by_id['menu']['menu_items']
    ])
    return (restaurant_with_menu_model)


def get_resto_by_id(restaurants,id) :
    i=0;
    i = 0
    res = {}
    while i<len(restaurants) and res=={}:
        if str(restaurants[i]['Id'])==str(id) :
            res = restaurants[i]
        i+=1
    return res 


