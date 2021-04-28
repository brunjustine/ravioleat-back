from flask import request
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests
from fuzzywuzzy import fuzz
import multiprocessing as mp
from app.services.restaurantService import RESTAURANT
import asyncio
from aiohttp import ClientSession


def get_deliveroo_restaurants(lat, lng):
    headers = {"X-Roo-Country": "uk", "Accept-Language": "en-en", "User": "Deliveroo-OrderApp/3.73.0",
               "Content-Type": "application/json"}
    try:
        params = {'lat': lat, 'lng': lng}
        url = "https://api.fr.deliveroo.com/orderapp/v2/restaurants"
        response_dict = requests.get(url, params=params, headers=headers)
        if (response_dict.status_code == 404) :
            res = []
        else : 
            restaurants = response_dict.json()
            restaurants_filtres = list(filter(lambda x: x["type"]=='restaurant' , restaurants["data"]))
            loop = get_or_create_eventloop()
            future = asyncio.ensure_future(run(restaurants,restaurants_filtres))
            restaurants_address = loop.run_until_complete(future)
            res = initResto(restaurants,restaurants_address)
        return res
    except Exception as e:
        print(e)
        abort(400, status=400, message="Bad Request", data=e.__str__())

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

async def run(restaurants,restaurants_filtres):
    restaurants_address = []
    async with ClientSession() as session:
        for restaurant in restaurants_filtres :
            res = asyncio.ensure_future(get_address(restaurant,session))
            restaurants_address.append(res)
        responses = await asyncio.gather(*restaurants_address)
        return responses
    

async def get_address(restaurant, session):
    id_restaurant = restaurant["id"]
    headers = {"X-Roo-Country":"fr", "Accept-Language":"fr-fr", "User":"Deliveroo-OrderApp/3.73.0","Content-Type":"application/json"}
    try :
        url = "https://api.fr.deliveroo.com/orderapp/v1/restaurants/"+str(id_restaurant)
        async with session.get(url,headers=headers) as response_dict: 
            if (response_dict.status == 404) :
                res = {}
            else :
                restaurant_by_id = await response_dict.json()
                res = {
                    "address": {
                        "City": restaurant_by_id["address"]["city"],
                        "FirstLine": restaurant_by_id["address"]["address1"],
                        "Postcode": restaurant_by_id["address"]["post_code"],
                        "Latitude": restaurant_by_id["address"]["coordinates"][1],
                        "Longitude": restaurant_by_id["address"]["coordinates"][0]

                    },
                    "UniqueName":restaurant_by_id["uname"].replace("-"," ")
                }
            return res
    except Exception as e:
                print(e)
                abort(400, status=400, message="Bad Request", data=e.__str__())


def initResto(restaurants, restaurants_address):
    listeRestos = []
    i=0
    for resto in restaurants["data"] :
        if resto['type'] == 'restaurant' :
            restaurant_model = RESTAURANT.copy()
            attributs = resto['attributes']
            restaurant_model.__setitem__("Api", "deliveroo")
            restaurant_model.__setitem__("Id", resto["id"])
            restaurant_model.__setitem__("Name", attributs["name"])
            restaurant_model.__setitem__("UniqueName", restaurants_address[i]["UniqueName"])
            restaurant_model.__setitem__("Address", restaurants_address[i]["address"])
            rating = attributs["rating_percentage"] if (attributs["rating_percentage"]==None) else (attributs["rating_percentage"])/20
            restaurant_model.__setitem__("Rating", {
                "Count":attributs["rating_formatted_count"],
                "StarRating":rating
            }) 
            restaurant_model.__setitem__("Description", "")
            restaurant_model.__setitem__("Url", "")
            restaurant_model.__setitem__("LogoUrl", attributs["image_url"])
            restaurant_model.__setitem__("DeliveryEtaMinutes", {
                "RangeLower": attributs["delivery_time"].split(" – ")[0],
                "RangeUpper": attributs["delivery_time"].split(" – ")[1]
            })
            restaurant_model.__setitem__("IsOpenNow", True)
            restaurant_model.__setitem__("DeliveryCost", attributs["delivery_fee"]["fractional"]/100)
            offers = listeOffres(resto,restaurants["included"])
            restaurant_model.__setitem__('Offers',offers)
            cuisineTypes = listeCategories(resto, restaurants["included"])
            restaurant_model.__setitem__("CuisineTypes", cuisineTypes)
            restaurant_model.__setitem__("PriceCategory", attributs["price_category"])
            listeRestos.append(restaurant_model)
            i+=1
    return(listeRestos)


def listeOffres(resto, toutesLesOffres) :
    resOffres = []
    for offreResto in resto["relationships"]["offers"]["data"] :
        res = next(offre for offre in toutesLesOffres if (offre["id"]==offreResto["id"] and offre["type"]==offreResto["type"]))
        resOffres.append({
            "Description": res["attributes"]["title"],
            "OfferId": res["id"]
        })
    return(resOffres)   

def listeCategories(resto, toutesLesCategories) :
    resCategories = []
    for categorieResto in resto["relationships"]["menu_tags"]["data"]: 
        res = next(categorie for categorie in toutesLesCategories if (categorie["id"]==categorieResto["id"] and categorie["type"]==categorieResto["type"]))
        if (int(res["id"])<200 and len(resCategories)<4):
            resCategories.append({
                "Id": res["id"],
                "Name": res["attributes"]["name"],
                "SeoName": res["attributes"]["uname"],
            })
    return(resCategories)


def search(lat,lng,mot) :
    restaurants = get_deliveroo_restaurants(lat,lng)
    restaurants_filtres = []
    mot = prepString(mot)
    for resto in restaurants : 
        nomResto = prepString(resto["Name"])
        if fuzz.token_set_ratio(mot,nomResto)>80 or fuzz.partial_ratio(mot,nomResto)>80:
            restaurants_filtres.append(resto)
    return restaurants_filtres


def prepString(_str):
    noise_list = [".", ",", "?", "!", ";"]
    for car in noise_list:
        _str = _str.replace(car, "")
    return _str.strip().lower()
