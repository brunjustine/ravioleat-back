from app import api

from app.resources.hello import HelloWorld

from app.resources.restaurants import *
from app.resources.restaurant import RestaurantById

api.add_resource(HelloWorld, "/")
api.add_resource(RestaurantsByLatLong, "/restaurants")
api.add_resource(RestaurantsByLatLongBySearch, "/restaurants/search")
api.add_resource(RestaurantById, "/restaurant/<restaurant_id>")

