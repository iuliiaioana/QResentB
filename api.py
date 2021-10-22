from flask import Flask,request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
        return "Hello", 200

api.add_resource(Home, '/home')