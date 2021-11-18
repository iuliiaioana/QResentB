  # QResent

QResent este o aplicatie de tip mobile ce vine in intampinarea problemelor digitalizarii sistemului educational. Aceasta este adresata atat studentilor, profesorilor cat si a adminitratorilor inregistrati. In functie de rolul utilizatorului aplicatia ofera diverse avantaje, precum: 
  - urmarire atenta a informatiilor de actualitate si a statisticilor oferite de fiecare materie
  - un sistem de identificare a studentilor prezenti in cadrul activitatiilor prin scanarea codurilor QR
  - configurarea materiilor (informatii utile: cerinte minime, intervale orare)
  - descarcarea listelor de prezente pentru orice activitate din trecut

## Tehnologii
[Frontend](https://github.com/iuliiaioana/QResentF)
  
[Backend](https://github.com/iuliiaioana/QResentB)
- [Pyton 3.8.10](https://www.python.org/downloads/release/python-3810/)
- [PEP8](https://www.python.org/dev/peps/pep-0008/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [PyJWT](https://pyjwt.readthedocs.io/en/stable/)
- [Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/)
- [gunicorn](https://docs.gunicorn.org/en/20.1.0/)
- [Deploy with Heroku](https://www.heroku.com/home)


Baza de Date:
  - [SQLite](https://www.sqlite.org/index.html)
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
  - [DB Browser for SQLite](https://sqlitebrowser.org/)

## Arhitectura BD



## API 

#### Scanare QR

```http
  POST /scan
```

| Body | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `activitate_id` | `string` |  **Required** Activitatea la care se doreste inregistrarea |
| `user_id` | `string` | **Required** Identificatorul utilizatorului |
| `locatie` | `string` |Locatia utilizatorului |
| `long` | `string` | Coordonata a locatiei |
| `lat` | `string` | Coordonata a locatiei  |

#### Generare QR bazata pe activitate
```http
  POST /generare_qr
```
| Body | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `profesor_id`      | `string` | **Required** Identificatorul profesorului|

#### Lista de prezenta

```http
  GET /prezenta/<int:activitate_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `activitate_id`      | `int` | **Required** Activitatea de la care se doreste prezenta |
| Body | Type     | Description                |
| `data` | `string` |  **Required** Data de la care se doreste prezenta|

#### Datiile disponibile pentru descarcarea listelor de prezenta
```http
  GET /dati/<int:activitate_id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `activitate_id`      | `int` | **Required** Activitatea de la care se doreste zilele disponibile pentru prezenta |

## Instalarea proiectului

```bash
  git clone https://github.com/iuliiaioana/QResentB.git
  cd QResentB
  pip install -r requirements.txt
  
```

## Documentatie

[Documentatie](https://docs.google.com/document/d/1TDuirgfmvJI1fCM7e3zsZY7MwS0vCSaKm8aOa0JYNRM/edit)    

## Echipa dezvoltare
- [@Iulia Anghel](https://github.com/iuliiaioana) PM
- [@Lucian Roinita](https://github.com/roinitalucian) TEAM LEAD
- [@Dragos Calin](https://github.com/CalinDS) FE Developer + Tester
- [@Roberta Calin](https://github.com/robertacalin) FE Developer
- [@Vlad Radutoiu](https://github.com/VladRadutoiu) FE Developer
- [@Lavinia Nedela](https://github.com/laviniamnedelea) BE Developer

