from collections import defaultdict

from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from flask.views import View
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from routes.login import Login

app = Flask(__name__)
cors = CORS(app)
JWTManager(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_PRIVATE_KEY'] = open('./rsa256.pem').read()
app.config['JWT_PUBLIC_KEY'] = open('./rsa256.pub').read()
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///qresent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

api = Api(app)
db = SQLAlchemy(app)
from models import user_prezenta,Activitati, Materie, PrezentaActivitate, User
db.create_all()

class Home(Resource):
    def get(self):
        return "Hello", 200


stats_data = {} # Prezentele unei activitati, generate de qr, cu data fisei de prezenta ca si cheie. Ca valori vom avea
# activitatea ca si cheie si ca valoare toate prezentele.

class Stats(Resource):
    def generate_statistics(self, prezenta_activitate_id):
        act_stat = defaultdict(list, {k: 0 for k in ('inceput', 'aleator', 'final')})
        prezenta_act = PrezentaActivitate.query.get(prezenta_activitate_id)
        act = Activitati.query.get(prezenta_act.id_activitate)

        start_treshold = (int(act.interval[3:5])- int(act.interval[0:2]))*6 # Primele minute care sunt csd "inceputul activitatii"
        end_treshold = (int(act.interval[3:5]) - int(act.interval[0:2]))*54 # Ultimele minute care sunt csd "sfarsitul activitatii"
        minut_generare =  (int(prezenta_act.ora_generare[0:2])-int(act.interval[0:2]))*60 + int(prezenta_act.ora_generare[3:5])

        id_act = act.id
        if id_act not in stats_data.keys():
            stats_data[id_act] = {}

        if minut_generare<=start_treshold:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['inceput'] = no

        elif minut_generare>=end_treshold:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['final'] = no

        else:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['aleator'] = no

    def get(self):
        return "Statistici"


api.add_resource(Home, '/home')
api.add_resource(Login, '/login')
api.add_resource(Stats, '/stats')


if __name__ == '__main__':
    app.run()