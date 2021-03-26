from flask import request
from flask_restful import Resource, reqparse, abort

from typing import Dict, List, Any

import requests


class restaurantByIDDeliverooResource(Resource):
    
    headers = {"X-Roo-Country":"fr", "Accept-Language":"fr-fr", "User":"Deliveroo-OrderApp/3.73.0","Content-Type":"application/json"}
    
    def get(self,id_restaurant) -> Dict[str, Any]:
        try :
            url = "https://api.fr.deliveroo.com/orderapp/v1/restaurants/"+str(id_restaurant)
            response_dict = requests.get(url,headers=self.headers)
            return({"status":200,"message":"OK","data":response_dict.json()})
        except Exception as e:
                    print(e)
                    abort(400)
    


