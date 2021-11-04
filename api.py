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
from models import materie_schema,user_schema,users_schema, ActivitatiMaterieSchema, UserSchema, user_prezenta,MaterieSchema,Activitati, Materie, PrezentaActivitate, User
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


class MaterieView(Resource):
    def post(self):
        nume = request.json['nume'] if 'nume' in request.json else None
        descriere = request.json['descriere'] if 'descriere' in request.json else None
        if 'id_profesor' in  request.json:
            profesor = User.query.filter(User.id == request.json['id_profesor']).one_or_none().id
        else:
            profesor=None
        materie = Materie(nume=nume, descriere=descriere,id_profesor=profesor)
        db.session.add(materie)
        db.session.commit()
        materie_schema = MaterieSchema()
        return materie_schema.jsonify(materie)

    def get(self):
        materii = Materie.query.all()
        response=[]
        activitati_schema= ActivitatiMaterieSchema(many=True)
        for materie in materii:
            activitate_materie = Activitati.query.filter(Activitati.id_materie == materie.id)
            response.append(
                {
                    'id': materie.id,
                    'descriere': materie.descriere,
                    'nume': materie.nume,
                    'id_profesor': materie.id_profesor,
                    'activitati' : activitati_schema.dump(activitate_materie)
                }
            )
        return response, 200

class MaterieDetail(Resource):
    def get(self, materie_id):
        materie = Materie.query.get_or_404(materie_id)
        activitati_schema= ActivitatiMaterieSchema(many=True)
        activitate_materie = Activitati.query.filter(Activitati.id_materie == materie.id)
        response = materie_schema.dump(materie)
        response['activitati']=activitati_schema.dump(activitate_materie)
        return response,200

    def put(self, materie_id):
        form_data = request.get_json()
        errors = materie_schema.validate(form_data)
        if errors:
            return '',400
        else:
            data=materie_schema.load(form_data)
            materie = Materie.query.get_or_404(materie_id)    
            for key, value in data.items():
                setattr(materie, key, value)
            db.session.commit()
            return materie_schema.jsonify(materie)


    def delete(self,materie_id):
        materie=Materie.query.get_or_404(materie_id)
        db.session.delete(materie)
        db.session.commit()
        return '',204

class UserView(Resource):
    def get(self):
        users = User.query.all()
        return users_schema.jsonify(users)
    
    def post(self):
        data=user_schema.load(request.get_json())
        user=User()
        for key, value in data.items():
            setattr(user, key, value)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)      

class UserDetail(Resource):
    def get(self,user_id):
        user = User.query.get_or_404(user_id)
        return user_schema.jsonify(user)

    def put(self,user_id):
        form_data = request.get_json()
        errors = user_schema.validate(form_data)
        if errors:
            return '',400
        else:
            data=user_schema.load(form_data)
            user = User.query.get_or_404(user_id)    
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
            return user_schema.jsonify(user)
    
    def delete(self,user_id):
        user=User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '',204



api.add_resource(Home, '/home')
api.add_resource(Login, '/login')
api.add_resource(Stats, '/stats')
api.add_resource(MaterieView, '/materii')
api.add_resource(MaterieDetail, '/materie/<int:materie_id>')
api.add_resource(UserView,'/users')
api.add_resource(UserDetail,'/user/<int:user_id>')


if __name__ == '__main__':
    app.run()