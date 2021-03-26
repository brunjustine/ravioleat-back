from flask import request
from flask_restful import Resource, reqparse, abort

from typing import Dict, List, Any

import requests

from app.services.restaurantService import RESTAURANT


def get_deliveroo_restaurants(lat, lng):
    headers = {"X-Roo-Country": "uk", "Accept-Language": "en-en", "User": "Deliveroo-OrderApp/3.73.0",
               "Content-Type": "application/json"}

    try:
        params = {'lat': lat, 'lng': lng}
        url = "https://api.fr.deliveroo.com/orderapp/v2/restaurants"
        response_dict = requests.get(url, params=params, headers=headers).json()
        res = initResto(response_dict)
        return res
    except Exception as e:
        print(e)
        abort(400, status=400, message="Bad Request", data=e.__str__())

# class restaurantDeliverooResource(Resource):
#
#     headers = {"X-Roo-Country":"uk", "Accept-Language":"en-en", "User":"Deliveroo-OrderApp/3.73.0","Content-Type":"application/json"}
#
#     def post(self):
#         try :
#             body_parser = reqparse.RequestParser(bundle_errors=True)
#             body_parser.add_argument('lat', type=float, required=True, help="Missing the latitude")
#             body_parser.add_argument('lng', type=float, required=True, help="Missing the longitutde")
#             args = body_parser.parse_args(strict=True)
#             lat = args['lat']
#             lng = args['lng']
#             params = {'lat':args['lat'], 'lng':args['lng']}
#             url = "https://api.fr.deliveroo.com/orderapp/v2/restaurants"
#             response_dict = requests.get(url,params=params,headers=self.headers).json()
#             res = initResto(response_dict)
#             return({"status":200,"message":"OK","data":res})
#         except Exception as e:
#                     print(e)
#                     abort(400)




def initResto(restaurants):
    listeRestos = []
    for resto in restaurants["data"] :
        if resto['type'] == 'restaurant' :
            restaurant_model = RESTAURANT.copy()
            attributs = resto['attributes']
            restaurant_model.__setitem__("Api", "deliveroo")
            restaurant_model.__setitem__("Id", resto["id"])
            restaurant_model.__setitem__("Name", attributs["name"])
            restaurant_model.__setitem__("UniqueName", None)
            restaurant_model.__setitem__("Address", None)
            rating = attributs["rating_percentage"] if (attributs["rating_percentage"]==None) else (attributs["rating_percentage"])/20
            restaurant_model.__setitem__("Rating", {
                "Count":attributs["rating_formatted_count"],
                "StarRating":rating
            }) 
            restaurant_model.__setitem__("Description", None)
            restaurant_model.__setitem__("Url", None)
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
        resCategories.append({
            "Id": res["id"],
            "Name": res["attributes"]["name"],
            "SeoName": res["attributes"]["uname"],
        })
    return(resCategories)


