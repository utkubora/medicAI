import tensorflow as tf
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
import torch

from flask import Flask, render_template, redirect, url_for, flash, request
from models import DiseaseChats,DiseaseMessage,db,app
from flask_login import current_user
from sqlalchemy import create_engine, Column, Integer, String, desc, asc

from ChatModels.constants import DISEASE_MAPPING

class ChatFunction:
    def __init__(self,model) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(model)
        self.inverse_mapping = {v: k for k, v in DISEASE_MAPPING.items()}
        
    def ask_to_model(self,symptoms, threshold=0.075):
        inputs = self.tokenizer(symptoms, return_tensors="tf", padding=True, truncation=True)
        prediction_output = self.model(inputs)
        prediction_probs = tf.nn.softmax(prediction_output.logits, axis=1)  # Apply softmax to get probabilities
        max_prob = tf.reduce_max(prediction_probs, axis=1).numpy()[0]
        predicted_label = tf.argmax(prediction_probs, axis=1).numpy()[0]
        
        if max_prob < threshold:
            return "I am not sure about your disease."
        else:
            disease_name = self.inverse_mapping[predicted_label]
            return disease_name
        
        
class ChatArea:
    
    @staticmethod
    def createChatArea():
        chatId = request.args.get('chat')
        if(chatId == None):
            #create a new chat
            context = {
                'chatId': None,
                'messages': []
            }
        else:
            #get a chat from history
            chat = DiseaseChats.query.filter_by(guid=chatId).first()
            messages = DiseaseMessage.query.filter_by(chatId=chat.guid).order_by(asc(DiseaseMessage.createDate)).all()
            context = {
            'chatId': chat.guid,
            'messages': messages
        }
        return render_template('chat_disease.html', **context)
    
    @staticmethod
    def send_message(chatId,data,fromWho):
        
        print(f"chatId : {chatId} && {chatId == None}")
        
        if(chatId == "None" or chatId == '' or chatId == None):
            #create a new chat
            chat = DiseaseChats(userId=current_user.guid, chatName=data, deleted=0)
            db.session.add(chat)
            db.session.commit()
            chatId = chat.guid
            
        print(f"chatId : {chatId} && {chatId == None}")
        print(f"data : {data}")
        print(f"fromWho : {fromWho}")
        
        message_from_user = DiseaseMessage(chatId=chatId,message=data,fromWho=fromWho)
        db.session.add(message_from_user)
        db.session.commit()
        
        return chatId