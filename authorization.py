from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, identity_changed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import urllib
from sqlalchemy_guid import GUID
import uuid
import re

from models import User, app, db

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not (re.fullmatch(regex, username.data)):
            #raise ValidationError('username is not an email adress!')
            return False
            
        user = User.query.filter_by(username=username.data).first()
        if user:
            #raise ValidationError('That username is taken. Please choose a different one.')
            return False
        return True

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
    
class MainFuncs:

    @staticmethod
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                
                if user.role == "admin":
                    return redirect(url_for('admin_panel'))
                elif user.role == "doctor":
                    return redirect(url_for('doctor_panel'))
                elif user.role == "patient":
                    return redirect(url_for('patient_panel'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
                
        return render_template('login.html', form=form)
    
    @staticmethod
    def register():
        form = RegistrationForm()
        try:
            if form.validate_on_submit():
                if(form.validate_username(form.username)):
                    hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
                    user = User(username=form.username.data, password=hashed_password, role='patient')
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('login'))
                else:
                    flash('Register unsuccessful. Please check username and password', 'danger')
            
        except Exception as e:
            print(e)
            flash('Register unsuccessful. Please check username and password', 'danger')
        
        return render_template('register.html', form=form)
    
    @staticmethod
    def logout():
        logout_user()
        identity_changed.send(app, identity=AnonymousIdentity())
        return redirect(url_for('login'))