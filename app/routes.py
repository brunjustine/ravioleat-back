from app import api

from app.resources.hello import HelloWorld
from app.resources.just_eat.restaurants import RestaurantsByLatLong

api.add_resource(HelloWorld, "/")
api.add_resource(RestaurantsByLatLong, "/restaurants")
