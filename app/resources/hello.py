from flask_restful import Resource, reqparse, abort
from app.resources.just_eat.utils import *
import requests


class HelloWorld(Resource):
    def get(self):
        return "Hello World"