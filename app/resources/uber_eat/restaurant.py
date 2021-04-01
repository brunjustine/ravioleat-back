from flask import request, jsonify, json
from flask_restful import Resource, reqparse, abort
from typing import Dict, List, Any
import requests

from app.services.restaurantWithMenuService import RESTAURANT_WITH_MENU
from app.resources.uber_eat.restaurants import get_uber_eat_restaurants


def get_uber_eat_restaurant_by_id(latitude, longitude, formatted_address, user_query, restaurant_id) -> Dict[str, Any]:
    uber_restaurants = get_uber_eat_restaurants(latitude, longitude, formatted_address, user_query)
    restaurant_with_menu_model = RESTAURANT_WITH_MENU.copy()
    for resto in uber_restaurants:
        if resto['Id']==restaurant_id:
            restaurant_with_menu_model = {x : resto[x] for x in resto.keys()}
            restaurant_with_menu_model.__setitem__("Menus", [])
    return restaurant_with_menu_model

