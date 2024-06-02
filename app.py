from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, UserNeed, Identity, AnonymousIdentity, identity_changed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import urllib
from sqlalchemy_guid import GUID
from sqlalchemy import create_engine, Column, Integer, String, desc, asc
import uuid

from models import User, app, db, MedicineChats,MedicineMessage,DiseaseChats,DiseaseMessage,LiteratureChats,LiteratureMessage
from authorization import MainFuncs

from ChatModels import MedicineChat,DiseaseChat,LiteratureChat

from ChatModels.constants import MEDICINE_MODEL_PATH,DISEASE_MODEL_PATH,LITERATURE_MODEL_PATH

login_manager = LoginManager(app)
login_manager.login_view = 'login'
principals = Principal(app)

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based permissions
admin_permission = Permission(RoleNeed('admin'))
doctor_permission = Permission(RoleNeed('doctor'))
patient_permission = Permission(RoleNeed('patient'))

# Doctor Pages permission
doctor_pages_permission = Permission(RoleNeed('admin'), RoleNeed('doctor'))

# Patient Pages permission
patient_pages_permission = Permission(RoleNeed('admin'), RoleNeed('doctor'), RoleNeed('patient'))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
        if current_user.role:
            identity.provides.add(RoleNeed(current_user.role))

@app.route("/register", methods=['GET', 'POST'])
def register():
    return MainFuncs.register()


@app.route("/login", methods=['GET', 'POST'])
def login():
    return MainFuncs.login()

@app.route('/logout')
@login_required
def logout():
    return MainFuncs.logout()

@app.route('/')
@login_required
def index():
    if current_user.role == "admin":
        return redirect(url_for('admin_panel'))
    elif current_user.role == "doctor":
        return redirect(url_for('doctor_panel'))
    elif current_user.role == "patient":
        return redirect(url_for('patient_panel'))
    else:
        return redirect(url_for('login'))



#-------------------------------- MAIN PAGES --------------------------------------------------------------------
@app.route('/admin')
@login_required
@admin_permission.require(http_exception=403)
def admin_panel():
    return render_template('admin.html')

class UsersForm(FlaskForm):
    submit = SubmitField('Search')
    search = StringField('Input', validators=[DataRequired()])
    
    
@app.route('/users-filtered/<filter>', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def users_panel_filtered(filter = ""):
    
    form=UsersForm()
    print(f"filter : {filter}" )
    
    if len(filter) == 0:
        users = User.query.order_by(desc(User.createDate)).all()
    else:
        users = User.query.filter_by(username=filter).order_by(desc(User.createDate)).all()
    
    context = {
            'users' : users
        }
    
    return render_template('users.html',form=form, **context)

@app.route('/users', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def users_panel():
    
    form=UsersForm()
    users = User.query.order_by(desc(User.createDate)).all()
    context = {
            'users' : users
        }
    
    return render_template('users.html',form=form, **context)

@app.route('/doctor')
@login_required
@doctor_permission.require(http_exception=403)
def doctor_panel():
    return render_template('doctor.html')

@app.route('/patient')
@login_required
@patient_permission.require(http_exception=403)
def patient_panel():
    return render_template('patient.html')
#-------------------------------- MAIN PAGES --------------------------------------------------------------------


#-------------------------------- MODEL PAGES --------------------------------------------------------------------
@app.route('/medicine-model')
@login_required
@doctor_pages_permission.require(http_exception=403)
def medicine_model():
    
    chats = []
    chats = MedicineChats.query.filter_by(userId=current_user.guid).order_by(desc(MedicineChats.createDate)).all()
    
    context = {
            'chats' : chats
        }
    
    return render_template('medicine_modal.html', **context)

@app.route('/disease-model')
@login_required
@patient_pages_permission.require(http_exception=403)
def disease_model():
    
    chats = []
    chats = DiseaseChats.query.filter_by(userId=current_user.guid).order_by(desc(DiseaseChats.createDate)).all()
    
    context = {
            'chats' : chats
        }
    
    return render_template('disease-model.html', **context)

@app.route('/literature-model')
@login_required
@doctor_pages_permission.require(http_exception=403)
def literature_model():
    
    chats = []
    chats = LiteratureChats.query.filter_by(userId=current_user.guid).order_by(desc(LiteratureChats.createDate)).all()
    
    context = {
            'chats' : chats
        }
    
    return render_template('literature-model.html', **context)
#-------------------------------- MODEL PAGES --------------------------------------------------------------------


#-------------------------------- CHAT PAGES --------------------------------------------------------------------
@app.route('/disease-chat')
@login_required
@doctor_pages_permission.require(http_exception=403)
def disease_chat_panel():
    return DiseaseChat.ChatArea.createChatArea()

@app.route('/medicine-chat')
@login_required
@patient_pages_permission.require(http_exception=403)
def medicine_chat_panel():
    return MedicineChat.ChatArea.createChatArea()

@app.route('/literature-chat')
@login_required
@doctor_pages_permission.require(http_exception=403)
def literature_chat_panel():
    return LiteratureChat.ChatArea.createChatArea()
#-------------------------------- CHAT PAGES --------------------------------------------------------------------


#-------------------------------- REST PAGES --------------------------------------------------------------------
@app.route('/submit-medicine', methods=['POST'])
@login_required
@doctor_pages_permission.require(http_exception=403)
def submit_medicine():
    model = MedicineChat.ChatFunction(MEDICINE_MODEL_PATH)
    
    data = request.form['data']
    chatId = request.form['chatId']
    
    try:
        chatId = MedicineChat.ChatArea.send_message(chatId,data,"user")
    except Exception as e:
        print(e)
    
    
    result = model.ask_to_model(data)
    
    try:
        chatId = MedicineChat.ChatArea.send_message(chatId,result,"model")
    except Exception as e:
        print(e)
    
    
    # Process the data if needed
    return jsonify({'message': 'Element added!', 'data': result})

@app.route('/submit-disease', methods=['POST'])
@login_required
@patient_pages_permission.require(http_exception=403)
def submit_disease():
    model = DiseaseChat.ChatFunction(DISEASE_MODEL_PATH)
    
    data = request.get_json().get('data')
    chatId = request.get_json().get('chatId')
    
    
    try:
        chatId = DiseaseChat.ChatArea.send_message(chatId,data,"user")
    except Exception as e:
        print(e)
    
    
    result = model.ask_to_model(data)
    try:
        chatId = DiseaseChat.ChatArea.send_message(chatId,result,"model")
    except Exception as e:
        print(e)
    
    
    
    # Process the data if needed
    return jsonify({ 'answer': result})

@app.route('/submit-literature', methods=['POST'])
@login_required
@doctor_pages_permission.require(http_exception=403)
def submit_literature():
    model = LiteratureChat.ChatFunction(LITERATURE_MODEL_PATH)
    
    
    data = request.get_json().get('data')
    chatId = request.get_json().get('chatId')
    
    print("data : " + str(data) )
    print("chatId : " + str(chatId) )
    
    try:
        chatId = LiteratureChat.ChatArea.send_message(chatId,data,"user")
    except Exception as e:
        print(e)
    
    
    result = model.ask_to_model(data)
    print(f"literature result = {result}" )
    try:
        chatId = LiteratureChat.ChatArea.send_message(chatId,result,"model")
    except Exception as e:
        print(e)
    
    # Process the data if needed
    return jsonify({ 'answer': result})

@app.route('/submit-user', methods=['POST'])
@login_required
@doctor_pages_permission.require(http_exception=403)
def submit_user():
    userId = request.form['userId']
    newRole = request.form['newRole']
    
    user = User.query.filter_by(guid=userId).first()
    user.role = newRole
    db.session.commit()
    
    # Process the data if needed
    return jsonify({'message': 'Element added!', 'data': newRole})
#-------------------------------- REST PAGES --------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
