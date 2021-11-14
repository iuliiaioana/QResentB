import re
from flask import json
from sqlalchemy.orm import validates
from flask_marshmallow import fields, Marshmallow
from marshmallow import Schema, fields
from api import db, app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import QueryableAttribute
ma = Marshmallow(app)

user_prezenta = db.Table('User_Prezenta',
                         db.Column('user_id', db.Integer, db.ForeignKey(
                             'user.id'), primary_key=True),
                         db.Column('prezenta_id', db.Integer, db.ForeignKey(
                             'prezenta_activitate.id'), primary_key=True)
                         )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    prenume = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    parola = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    grupa = db.Column(db.String(20), nullable=False)
    prezente = db.Column(db.String(100), nullable=False)
    prezenta_activ = db.relationship('PrezentaActivitate', secondary=user_prezenta, lazy='subquery',
                                     backref=db.backref('useri', lazy='joined'))

    def __init__(self, nume='', prenume='', rol='', parola='', email='@stud.acs.pub.ro', grupa='', prezente=''):
        self.nume = nume
        self.prenume = prenume
        self.rol = rol
        self.parola = parola
        self.email = email
        self.grupa = grupa
        self.prezente = prezente

    @validates('email')
    def validare_email(self, key, address):
        if '@' not in address:
            raise ValueError("Failed email validation.")
        return address


class PrezentaActivitate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ora_validare = db.Column(db.String(100), nullable=False)
    id_activitate = db.Column(db.Integer, db.ForeignKey(
        'activitate.id'), nullable=False)
    data = db.Column(db.String(100), nullable=False)
    locatie = db.Column(db.String(100), nullable=False, default='')
    lat = db.Column(db.String(100), nullable=False, default='')
    long = db.Column(db.String(100), nullable=False, default='')

    def __init__(self, ora_validare, id_activitate, data, locatie, lat, long):
        self.ora_validare = ora_validare
        self.data = data
        self.id_activitate = id_activitate
        self.locatie = locatie
        self.lat = lat
        self.long = long


class Activitate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interval = db.Column(db.String(100), nullable=False)
    id_materie = db.Column(db.Integer, db.ForeignKey(
        'materie.id'), nullable=False)
    zi = db.Column(db.String(100), nullable=False)
    grupa = db.Column(db.String(20), nullable=False)
    prezente = db.relationship(
        'PrezentaActivitate', backref='activitate_univ', cascade="all,delete", lazy=True)

    def __init__(self, interval, zi='', grupa=''):
        self.interval = interval
        self.zi = zi
        self.grupa = grupa

    @validates('interval')
    def validare_interval(self, key, interval):
        pattern = re.compile(
            "^([0[0-9]|1[0-9]|2[0-3]):([0[0-9]|1[0-9]|2[0-3])$")
        if not pattern.match(interval):
            raise ValueError("Failed interval validation.")
        return interval


class Materie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descriere = db.Column(db.String(300), nullable=False,
                          default="Disciplina universitara.")
    id_profesor = db.Column(db.Integer, foreign_key=True)
    nume = db.Column(db.String(100), nullable=False)
    activitati = db.relationship(
        'Activitate', backref='materie_univ', lazy=True)

    def __init__(self, descriere=None, id_profesor=None, nume=None):
        self.descriere = descriere
        self.id_profesor = id_profesor
        self.nume = nume


class ActivitatiMaterieSchema(ma.Schema):
    class Meta:
        fields = ("id", "interval", "zi", "grupa")
        ordered = True


class MaterieSchema(ma.Schema):
    class Meta:
        fields = ("id", "descriere", "id_profesor", "nume")
        ordered = True


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "nume", "prenume", "rol", "parola",
                  "email", "grupa", "prezente")
        ordered = True


class ActivitateSchema(ma.Schema):
    class Meta:
        fields = ("id", "interval", "zi", "grupa", "id_materie")
        ordered = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
materie_schema = MaterieSchema()
activitate_schema = ActivitateSchema()
