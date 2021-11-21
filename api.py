import copy
from collections import defaultdict
import pandas as pd
from datetime import datetime,timedelta
import requests
import json
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from flask.views import View
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required
from flask_sqlalchemy import SQLAlchemy

from marshmallow import Schema, fields, ValidationError, pre_load

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
from models import Activitate,activitate_schema, user_prezenta, materie_schema,user_schema,users_schema, ActivitatiMaterieSchema, UserSchema, user_prezenta,MaterieSchema,Activitate, Materie, PrezentaActivitate, User
db.create_all()

stats_data = {} # Prezentele unei activitati, generate de qr, cu data fisei de prezenta ca si cheie. Ca valori vom avea
# activitatea ca si cheie si ca valoare toate prezentele.

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user_id = self.check_credentials(email, password)
        if  user_id > 0:
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)

            return jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_id
                }
            )

        return "bad credentials", 401

    def check_credentials(self, email, password):
        user = User.query.filter(User.email == email).one_or_none()
        return user.id if user.parola == password else -1

class Stats(Resource):
    def generate_statistics_qr_activity(self, prezenta_activitate_id):
        act_stat = defaultdict(list, {k: 0 for k in ('inceput', 'aleator', 'final')})
        prezenta_act = PrezentaActivitate.query.get_or_404(prezenta_activitate_id)
        act = Activitate.query.get_or_404(prezenta_act.id_activitate)

        start_treshold = (int(act.interval[3:5])- int(act.interval[0:2]))*6 # Primele minute care sunt csd "inceputul activitatii"
        end_treshold = (int(act.interval[3:5]) - int(act.interval[0:2]))*54 # Ultimele minute care sunt csd "sfarsitul activitatii"
        minut_generare =  (int(prezenta_act.ora_validare[0:2])-int(act.interval[0:2]))*60 + int(prezenta_act.ora_validare[3:5])

        id_act = act.id
        if id_act not in stats_data.keys():
            stats_data[id_act] = defaultdict(int)

        if minut_generare<=start_treshold:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['inceput'] += no

        elif minut_generare>=end_treshold:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['final'] += no

        else:
            no = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id==prezenta_activitate_id).count()
            if str(prezenta_act.data) not in stats_data[id_act].keys():
                stats_data[id_act][str(prezenta_act.data)] = act_stat
            stats_data[id_act][str(prezenta_act.data)]['aleator'] += no
        return stats_data

    # Cati useri au fost prezenti in total intr-o zi la o anumita activitate, indiferent de momentul in care s-au marcat prezenti.
    def generate_statistics_users_per_activity_date(self,id_activitate,data):
        id_prezente = db.session.query(PrezentaActivitate).filter(PrezentaActivitate.id_activitate == id_activitate and PrezentaActivitate.data == data).all()
        prezente = []
        for i in id_prezente:
            entries_user_prezenta = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id == i.id).all()
            if entries_user_prezenta:
                prezente += [x[0] for x in entries_user_prezenta]
        return len(set(prezente))

    # Cate materii preda fiecare profesor
    def generate_statistics_prof_per_subject(self): # {id_prof : no_subjects}
        id_profs = list(set(db.session.query(Materie.id_profesor).all()))
        prof_subj = {}
        for i in id_profs:
            id_subjects = db.session.query(Materie).filter(Materie.id_profesor == i[0]).all()
            profesor = db.session.query(User.nume, User.prenume).filter(User.id==i[0]).all()
            nume_profesor = profesor[0][0] + " " + profesor[0][1]
            prof_subj[nume_profesor] = len(id_subjects)
        return prof_subj

    # Cati elevi de la fiecare grupa au fost prezenti la o activitate (in orice moment al ei)
    def generate_statistics_users_gr_per_activity_date(self, id_activitate, data): # {grupa : nr_participanti}
        id_prezente = db.session.query(PrezentaActivitate).filter(
            PrezentaActivitate.id_activitate == id_activitate and PrezentaActivitate.data == data).all()
        gr_no = defaultdict(int) # dictionar corespunzator grupei si nr de participanti
        students_id = []
        for i in id_prezente:
            entries_user_prezenta = db.session.query(user_prezenta).filter(user_prezenta.c.prezenta_id == i.id).all() # Cautam inregistrarile de prezente de pe prezenta data
            for k in entries_user_prezenta:
                students_id.append(k.user_id)
        students_id = set(students_id)
        for k in students_id:
            entry = db.session.query(User).filter(User.id == k).all()
            gr_no[entry[0].grupa] += 1
        return gr_no

    def post(self):
        interval=request.json['interval']
        zi = request.json['zi']
        id_prof = request.json['id_prof']
        materie = request.json['materie']
        data = request.json['data']

        response = {}
        try:
            id_materie = db.session.query(Materie).filter(Materie.id_profesor == id_prof).filter(Materie.nume == materie).all()[0].id
            id_activitate = db.session.query(Activitate).filter(Activitate.interval==interval).filter(Activitate.zi==zi).filter(Activitate.id_materie==id_materie).all()[0].id
            id_generariPrezente = db.session.query(PrezentaActivitate).filter(PrezentaActivitate.id_activitate==id_activitate).filter(PrezentaActivitate.data==data).all()
        except:
            raise("404: NOT FOUND")

        for i in id_generariPrezente:
            self.generate_statistics_qr_activity(i.id)
        final_stats = copy.deepcopy(stats_data)
        stats_data.clear()
        response['ActDataStatus'] = final_stats
        stats_total = self.generate_statistics_users_per_activity_date(id_activitate,data)
        response['TotalPerAct'] = stats_total

        stats_prof = self.generate_statistics_prof_per_subject()
        response['ProfSubNo'] = stats_prof

        stats_grupa = self.generate_statistics_users_gr_per_activity_date(id_activitate,data)
        response['GrupaPerAct'] = stats_grupa

        return response, 200

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
            activitate_materie = Activitate.query.filter(Activitate.id_materie == materie.id)
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
        activitate_materie = Activitate.query.filter(Activitate.id_materie == materie.id)
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
    @jwt_required()
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

class ActivitateView(Resource):
    def get(self):
        activitati = Activitate.query.all()
        response=[]
        for activitate in activitati:
                activitate_materie = Materie.query.get(activitate.id_materie)
                response.append(
                    {
                        'id': activitate.id,
                        'interval': activitate.interval,
                        'zi': activitate.zi,
                        'grupa': activitate.grupa,
                        'materie' : materie_schema.dump(activitate_materie)
                    }
                )
        return response, 200
    
    def post(self):
        """
        *Required request body: interval <hour:hour>, id_materie ! , zi, grupa
        """
        data = request.get_json()
        try:
            data=activitate_schema.load(request.get_json())
            interval = data['interval'] if 'interval' in data else None
            activitate=Activitate(interval)
            for key, value in data.items():
                setattr(activitate, key, value)
            db.session.add(activitate)
            db.session.commit()
            return activitate_schema.jsonify(activitate)  
        except:   #da integrity error daca nu dai id materie - pana se pune required pe FE las asa 
            return '',400


class ActivitateDetail(Resource):
    def get(self,activitate_id):
        activitate = Activitate.query.get_or_404(activitate_id)
        return activitate_schema.jsonify(activitate)
    
    def put(self,activitate_id):
        form_data = request.get_json()
        errors = activitate_schema.validate(form_data)
        if errors:
            return '',400
        else:
            data=activitate_schema.load(form_data)
            activitate = Activitate.query.get_or_404(activitate_id)    
            for key, value in data.items():
                setattr(activitate, key, value)
            db.session.commit()
            return activitate_schema.jsonify(activitate)
    
    def delete(self,activitate_id):
        activitate=Activitate.query.get_or_404(activitate_id)
        db.session.delete(activitate)
        db.session.commit()
        return '',204

class Scan(Resource):
    """
    *Required request body: activitate_id, user_id, ora_qr <format:2021-11-14T17:13:53.883Z> 
    optional: locatie, lat, long

    """
    def post(self):
        activitate=request.json['activitate_id']
        date_format_str = '%Y-%m-%dT%H:%M:%S'
        ora_qr_dt=pd.to_datetime(request.json['ora_qr'][:-1], format=date_format_str)
        user_id=request.json['user_id']
        oras=request.json['locatie'] if 'locatie' in request.json else None
        lat=request.json['lat'] if 'lat' in request.json else None
        long=request.json['long'] if 'long' in request.json else None
        now = datetime.now()

        zi=now.strftime("%d.%m.%Y")
        ora=now.strftime("%H:%M")
        if (now-ora_qr_dt).total_seconds() / 60 < 15: #mai mult de 5 min nu permitem scanarea

            prez_act=PrezentaActivitate(ora_validare=ora,id_activitate=activitate, data=zi,locatie=oras, lat=lat, long=long)
            db.session.add(prez_act)
            user=User.query.get_or_404(user_id)
            user.prezenta_activ.append(prez_act)
            db.session.commit()
            return 'Scanare cu succes!',200
            
 
        return 'Scanare esuata!',403

class ListaPrezenta(Resource):
    """
    Export to File
    """
    def get(self, activitate_id,data_selectata):
        response={}
        a = Activitate.query.get_or_404(activitate_id)
        response['interval_activitate'] = a.interval
        m = Materie.query.get_or_404(a.id_materie)
        response['materie'] = m.nume
        response['zi'] = a.zi
        response['grupa'] = a.grupa
        response['student'] = []
        for activitate_prezenta in a.prezente:
            student = {}
            user = User.query.join(user_prezenta).join(PrezentaActivitate).filter((user_prezenta.c.user_id == User.id) & (user_prezenta.c.prezenta_id == activitate_prezenta.id) & (activitate_prezenta.data == data_selectata)).first()
            if user:
                student['nume'] = user.nume + " " + user.prenume
                student['email'] = user.email
                student['ora_validare'] = activitate_prezenta.ora_validare
                student['locatie'] = activitate_prezenta.locatie + "(lat: " + activitate_prezenta.lat + " long: " + activitate_prezenta.long + ")"
                response['student'].append(student)
        return response,200

class ListaPrezentaData(Resource):
    """
    Get all dates for a past activity
    """
    def get(self,activitate_id):
        prezenta_zi=PrezentaActivitate.query.filter(PrezentaActivitate.id_activitate==activitate_id).group_by(PrezentaActivitate.data)
        response=list(zi.data for zi in prezenta_zi)
        return response,200
        
class GenerateQR(Resource):
    def post(self):
        profesor=request.json['profesor_id']
        
        zi_dict={'Monday' : 'luni','Tuesday' : 'marti','Wednesday' : 'miercuri','Thursday' : 'joi','Friday' : 'vineri','Sunday' : 'duminica'}
        now = datetime.now()
        ora=now.strftime("%H")
        ziua=zi_dict[now.strftime("%A")]
        activitati= Activitate.query.filter((Activitate.id_materie == Materie.id) & (Materie.id_profesor == profesor) & (Activitate.zi == ziua)).all()

        for act in activitati:
            interval= str(act.interval).split(":")
            if int(interval[0]) <= int(ora) and int(interval[0]) + 2 >= int(ora):
                return {'activitate_id': act.id}, 200
        return 'Activitate neinregistrata in acest interval orar',404

class GasesteActivitate(Resource):
    """
    Dupa profesor_id ofera toate activitatiile aferente materiilor pe care le preda 

    Returneaza: { <materie_nume>_<zi>_<interval> : <activitate_id> ...}
    """
    def get(self,profesor_id):
        activitati_profesor={}
        materii_profesor = Materie.query.filter(Materie.id_profesor == profesor_id).all()
        for materie in materii_profesor:
            activitati_materie = Activitate.query.filter(Activitate.id_materie == materie.id).all()
            for activitate in activitati_materie:
                key= materie.nume + '_' + activitate.zi + '_' + activitate.interval
                activitati_profesor[key]= activitate.id
        return activitati_profesor, 200

class Calendar(Resource):
    def get(self):
        pass

    def post(self):
        pass

api.add_resource(Scan, '/scan')
api.add_resource(Login, '/login')
api.add_resource(GenerateQR, '/generare_qr')
api.add_resource(ListaPrezenta, '/prezenta/<int:activitate_id>/<string:data_selectata>')
api.add_resource(ListaPrezentaData, '/dati/<int:activitate_id>')
api.add_resource(Stats, '/stats')
api.add_resource(MaterieView, '/materii')
api.add_resource(MaterieDetail, '/materie/<int:materie_id>')
api.add_resource(UserView,'/users')
api.add_resource(UserDetail,'/user/<int:user_id>')
api.add_resource(ActivitateView,'/activitati')
api.add_resource(ActivitateDetail,'/activitate/<int:activitate_id>')
api.add_resource(GasesteActivitate,'/activitati_profesor/<int:profesor_id>')
api.add_resource(Calendar, '/calendar')