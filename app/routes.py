from app import api

from app.resources.hello import HelloWorld
from app.resources.uber_eat.restaurant_uber import RestaurantUberCategoryResource, RestaurantUberResource, RestaurantUberSearchResource, RestaurantUberByIdResource
#from app.resources.uber_eat.restaurant_uber import RestaurantUberCategoryResource, RestaurantUberResource, RestaurantUberSearchResource


api.add_resource(HelloWorld, "/")
api.add_resource(RestaurantUberCategoryResource, "/restaurants/uber/categories")
api.add_resource(RestaurantUberSearchResource, "/restaurants/uber/search")
api.add_resource(RestaurantUberResource, "/restaurants/uber")
api.add_resource(RestaurantUberByIdResource, "/restaurants/uber/<restaurant_id>")