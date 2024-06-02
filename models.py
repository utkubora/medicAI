from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, identity_changed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import urllib
from sqlalchemy_guid import GUID
import uuid

from ChatModels.constants import APP_SECRET_KEY,CONNECTION_STRING_DRIVER,CONNECTION_STRING_SERVER,CONNECTION_STRING_DATABASE,CONNECTION_STRING_USER

app = Flask(__name__)

app.config['SECRET_KEY'] = APP_SECRET_KEY

# MSSQL configuration
"""
params = urllib.parse.quote_plus(CONNECTION_STRING_DRIVER,
                                 CONNECTION_STRING_SERVER,
                                 CONNECTION_STRING_DATABASE,
                                 CONNECTION_STRING_USER)
                                 """
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={CONNECTION_STRING_DRIVER + CONNECTION_STRING_SERVER + CONNECTION_STRING_DATABASE + CONNECTION_STRING_USER}"


db = SQLAlchemy(app)

#db.create_all()


# User model

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    username = db.Column(db.String(5000), unique=True, nullable=False)
    password = db.Column(db.String(5000), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    deleted = db.Column(db.Integer, nullable=True,default=0)
    
    
class MedicineChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    userId = db.Column(GUID, nullable=True)
    chatName = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)

class MedicineMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    chatId = db.Column(GUID, nullable=True)
    message = db.Column(db.String(5000))
    fromWho = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)
    
    
    
class DiseaseChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    userId = db.Column(GUID, nullable=True)
    chatName = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)

class DiseaseMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    chatId = db.Column(GUID, nullable=True)
    message = db.Column(db.String(5000))
    fromWho = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)
    
    
    
class LiteratureChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    userId = db.Column(GUID, nullable=True)
    chatName = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)

class LiteratureMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(GUID, default=uuid.uuid4, unique=True)
    createDate = db.Column(DateTime, default=datetime.utcnow)
    chatId = db.Column(GUID, nullable=True)
    message = db.Column(db.String(5000))
    fromWho = db.Column(db.String(50))
    deleted = db.Column(db.Integer, nullable=True,default=0)