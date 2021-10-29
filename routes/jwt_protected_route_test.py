from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

class JWT_test(Resource):
    @jwt_required()
    def get(self):
        return "merge jwt"