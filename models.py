import jwt
from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)  # new email field
    password_hash = db.Column(db.String(120))

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email  # set the email
        self.password_hash = password_hash
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def get_reset_password_token(self, expires_sec=1800):
        reset_token = jwt.encode(
            {"user_id": self.id, "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_sec)},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token  # No need to decode the token, it's already a string
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=timedelta(seconds=10),
                algorithms=["HS256"]
            )['user_id']
        except:
            return None
        return User.query.get(user_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

def save_user_to_database(username, email, password_hash):  # add email parameter
    user = User(username, email, password_hash)  # pass email to User constructor
    db.session.add(user)
    db.session.commit()

def get_user_from_database(user_id):
    user = User.query.get(user_id)
    return user

class Recipe(db.Model):
    spoonacular_id = db.Column(db.Integer, primary_key=True)  # new primary key
    data = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    message = db.Column(db.Text)

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message