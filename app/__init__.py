from flask import Flask
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)

from app import routes

cors = CORS(app, resources={r"/*": {"origins": "*"}})
