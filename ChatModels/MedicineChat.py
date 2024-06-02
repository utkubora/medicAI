from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

from flask import Flask, render_template, redirect, url_for, flash, request
from models import MedicineChats,MedicineMessage,db,app
from flask_login import current_user
from sqlalchemy import create_engine, Column, Integer, String, desc, asc

from ChatModels.constants import DRUG_MAPPING

class ChatFunction:
    def __init__(self,model) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModelForSequenceClassification.from_pretrained(model, from_tf=False, torch_dtype=torch.float16, use_safetensors=True)
        
    
    def ask_to_model(self,question):
        inputs = self.tokenizer(question, return_tensors="pt", truncation=True, padding=True)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)
        predicted_label = predictions.cpu().numpy()[0]
        return DRUG_MAPPING[str(predicted_label)]
        
        
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
            chat = MedicineChats.query.filter_by(guid=chatId).first()
            messages = MedicineMessage.query.filter_by(chatId=chat.guid).order_by(asc(MedicineMessage.createDate)).all()
            context = {
            'chatId': chat.guid,
            'messages': messages
        }
        return render_template('chat_medicine.html', **context)
    
    @staticmethod
    def send_message(chatId,data,fromWho):
        
        print(f"chatId : {chatId} && {chatId == None}")
        
        if(chatId == "None" or chatId == '' or chatId == None):
            #create a new chat
            chat = MedicineChats(userId=current_user.guid, chatName=data, deleted=0)
            db.session.add(chat)
            db.session.commit()
            chatId = chat.guid
        
        message_from_user = MedicineMessage(chatId=chatId,message=data,fromWho=fromWho)
        db.session.add(message_from_user)
        db.session.commit()
        return chatId