from app import api

from app.resources.hello import HelloWorld
from app.resources.deliveroo.restaurants import restaurantDeliverooResource
from app.resources.deliveroo.restaurant import restaurantByIDDeliverooResource
from app.resources.just_eat.restaurants import *
from app.resources.just_eat.restaurant import RestaurantByID

api.add_resource(HelloWorld, "/")
api.add_resource(restaurantDeliverooResource, '/restaurantDeliveroo')
api.add_resource(restaurantByIDDeliverooResource, '/restaurantDeliveroo/<int:id_restaurant>')


api.add_resource(RestaurantsByLatLong, "/restaurants")
#api.add_resource(RestaurantsByLatLongSearch, "/restaurants/search")
api.add_resource(RestaurantByID, "/restaurant/<int:restaurant_id>")
