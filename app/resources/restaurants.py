from flask_restful import Resource, reqparse, abort
from app.resources.just_eat.restaurants import get_just_eat_restaurants, get_just_eat_restaurant_search
from app.resources.deliveroo.restaurants import get_deliveroo_restaurants, search
from app.resources.uber_eat.restaurants import get_uber_eat_restaurants
from multiprocessing import Process, Queue


class RestaurantsByLatLong(Resource):
    def post(self):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument('formattedAddress', type=str, required=True, help="Missing the address ")
        body_parser.add_argument('userQuery', type=str, required=True, help="Missing the user query ")

        # Accepted only if these two parameters are strictly declared in body else raise exception
        args = body_parser.parse_args(strict=True)

        try:
            lat = args['lat']
            lon = args['lon']
            formatted_address = args['formattedAddress']
            user_query = args['userQuery']

            restaurants = []

            q = Queue()

            p1 = Process(target=get_just_eat,args=(lat,lon,q))
            p2 = Process(target=get_deliveroo,args=(lat,lon,q))
            p3 = Process(target=get_uber_eat,args=(lat,lon,formatted_address, user_query,q))
            p1.start()
            p2.start()
            p3.start()
            for i in range(3):
                restaurants.extend(q.get()) 
            return {"status": 200, "message": "OK", "data": restaurants}

        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data=e.__str__())
        
def get_just_eat(lat, lon,q):
    q.put(get_just_eat_restaurants(lat, lon))

def get_deliveroo(lat, lon,q):
    q.put(get_deliveroo_restaurants(lat, lon))

def get_uber_eat(lat, lon, formatted_address, user_query,q):
    q.put(get_uber_eat_restaurants(lat, lon, formatted_address, user_query))


class RestaurantsByLatLongBySearch(Resource):
    def post(self):
        body_parser = reqparse.RequestParser()
        body_parser.add_argument('lat', type=str, required=True, help="Missing the latitude")
        body_parser.add_argument('lon', type=str, required=True, help="Missing the longitude")
        body_parser.add_argument('searchTerm', type=str, required=True, help="Missing the searchTerm")
        body_parser.add_argument('formattedAddress', type=str, required=True, help="Missing the address ")
        # Accepted only if these two parameters are strictly declared in body else raise exception
        args = body_parser.parse_args(strict=True)

        try:
            lat = args['lat']
            lon = args['lon']
            search_term = args['searchTerm']
            formatted_address = args['formattedAddress']

            restaurants = []
            q = Queue()
            
            p1 = Process(target=get_just_eat_search,args=(lat,lon,search_term,q))
            p2 = Process(target=get_deliveroo_search,args=(lat,lon,search_term,q))
            p3 = Process(target=get_uber_eat_search,args=(lat,lon,formatted_address, search_term,q))
            p1.start()
            p2.start()
            p3.start()
            for i in range(3):
                restaurants.extend(q.get()) 
            return {"status": 200, "message": "OK", "data": restaurants}

        except Exception as e:
            print(e)
            abort(400, status=400, message="Bad Request", data=e.__str__())

def get_just_eat_search(lat, lon,search_term,q):
    q.put(get_just_eat_restaurant_search(lat, lon, search_term))

def get_deliveroo_search(lat, lon,search_term,q):
    q.put(search(lat, lon, search_term))

def get_uber_eat_search(lat, lon, formatted_address, search_term,q):
    q.put(get_uber_eat_restaurants(lat, lon, formatted_address, search_term))