from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required

class Login(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if self.check_credentials(email, password):
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)

            return jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            )

        return "bad credentials", 401

    def check_credentials(self, email, password):
        return email == 'admin' and password == 'admin'