from api import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nume = db.Column(db.String(100), nullable=False)
    prenume = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    parola = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    grupa = db.Column(db.String(20), nullable=False)
    prezente = db.Column(db.String(100), nullable=False)

    def __init__(self, nume, prenume, rol, parola, email, grupa, prezente):
        self.nume = nume
        self.prenume = prenume
        self.rol = rol
        self.parola = parola
        self.email = email
        self.grupa = grupa
        self.prezente = prezente


class Prezenta_Activitate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ora_generare = db.Column(db.DateTime, nullable=False)
    id_activitate = db.Column(db.Integer, db.ForeignKey('activitati.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)

    def __init__(self, ora_generare, id_activitate, data):
        self.ora_generare = ora_generare
        self.id_activitate = id_activitate
        self.data = data

class Activitati(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interval = db.Column(db.String(100), nullable=False)
    id_materie = db.Column(db.Integer, db.ForeignKey('materie.id'), nullable=False)
    zi = db.Column(db.String(100), nullable=False)
    grupa = db.Column(db.String(20), nullable=False)
    prezente = db.relationship('Prezenta_Activitate', backref='activitati', lazy=True)

    def __init__(self, interval, id_materie, zi, grupa, prezente):
        self.interval = interval
        self.id_materie = id_materie
        self.zi = zi
        self.grupa = grupa
        self.prezente = prezente


class Materie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descriere = db.Column(db.String(300), nullable=False, default="Disciplina universitara.")
    id_profesor = db.Column(db.Integer, foreign_key=True)  #
    nume = db.Column(db.String(100), nullable=False)
    prezente = db.relationship('Activitati', backref='materie', lazy=True)

    def __init__(self, descriere, id_profesor, nume):
        self.descriere = descriere
        self.id_profesor = id_profesor
        self.nume = nume


# Table for many to many relationship.
user_prezenta = db.Table('User_Prezenta',
                db.Column('user_id', db.Integer, db.ForeignKey(User.id), primary_key=True),
                db.Column('prezenta_id', db.Integer, db.ForeignKey(Prezenta_Activitate.id), primary_key=True)
                )
