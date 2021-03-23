from app import api

from app.resources.hello import HelloWorld

api.add_resource(HelloWorld, "/")