from api import db

user_prezenta = db.Table('User_Prezenta',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                db.Column('prezenta_id', db.Integer, db.ForeignKey('prezenta_activitate.id'), primary_key=True)
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
                           backref=db.backref('useri', lazy=True))
    def __init__(self, nume, prenume, rol, parola, email, grupa, prezente):
        self.nume = nume
        self.prenume = prenume
        self.rol = rol
        self.parola = parola
        self.email = email
        self.grupa = grupa
        self.prezente = prezente

class PrezentaActivitate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ora_generare = db.Column(db.DateTime, nullable=False)
    id_activitate = db.Column(db.Integer, db.ForeignKey('activitati.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)

    def __init__(self, ora_generare, data):
        self.ora_generare = ora_generare
        self.data = data

class Activitati(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interval = db.Column(db.String(100), nullable=False)
    id_materie = db.Column(db.Integer, db.ForeignKey('materie.id'), nullable=False)
    zi = db.Column(db.String(100), nullable=False)
    grupa = db.Column(db.String(20), nullable=False)
    prezente = db.relationship('PrezentaActivitate', backref='activitati_univ', lazy=True)

    def __init__(self, interval, zi, grupa):
        self.interval = interval
        self.zi = zi
        self.grupa = grupa

class Materie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descriere = db.Column(db.String(300), nullable=False, default="Disciplina universitara.")
    id_profesor = db.Column(db.Integer, foreign_key=True)
    nume = db.Column(db.String(100), nullable=False)
    activitati = db.relationship('Activitati', backref='materie_univ', lazy=True)

    def __init__(self, descriere, id_profesor, nume):
        self.descriere = descriere
        self.id_profesor = id_profesor
        self.nume = nume