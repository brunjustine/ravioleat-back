from app import api

from app.resources.hello import HelloWorld
from app.resources.deliveroo.restaurants import restaurantDeliverooResource
from app.resources.deliveroo.restaurant import restaurantByIDDeliverooResource

api.add_resource(HelloWorld, "/")
api.add_resource(restaurantDeliverooResource, '/api/restaurantDeliveroo')
api.add_resource(restaurantByIDDeliverooResource, '/api/restaurantDeliveroo/<int:id_restaurant>')