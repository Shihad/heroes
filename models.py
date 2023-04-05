from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import random

db = SQLAlchemy()

class Personage(db.Model):
    __tablename__="personages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    hp = db.Column(db.Integer)
    max_hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defence = db.Column(db.Integer)
    state = db.Column(db.String(20))

    def __init__(self, name):
        self.name=name
        self.max_hp = random.randint(100,110)
        self.hp=self.max_hp
        self.attack=10
        self.defence=10
        self.state='idle'

    def __repr__(self):
        return f"{self.name} has {self.hp} of {self.max_hp}"

    def json(self):
        hero={"attack":self.attack,
              "defence":self.defence,
              "state":self.state,
              "hp":self.hp,
              "max_hp":self.max_hp,
              "name":self.name}

        return hero

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True)
    mail = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(150))

    def __init__(self, login, mail,password):
        self.login=login
        self.mail=mail
        self.set_password(password)

    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)