from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from flask.views import View
from flask_jwt_extended import JWTManager

from routes.login import Login

app = Flask(__name__)
cors = CORS(app)
JWTManager(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_PRIVATE_KEY'] = open('./rsa256.pem').read()
app.config['JWT_PUBLIC_KEY'] = open('./rsa256.pub').read()

api = Api(app)

class Home(Resource):
    def post(self):
        return "Hello", 200

api.add_resource(Home, '/home')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run()