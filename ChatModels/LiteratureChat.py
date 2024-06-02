from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from models import LiteratureChats,LiteratureMessage,db,app
from flask_login import current_user
from sqlalchemy import create_engine, Column, Integer, String, desc, asc
import requests
from bs4 import BeautifulSoup

class ChatFunction:
    def __init__(self,model) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-large')
        self.model = AutoModelForCausalLM.from_pretrained(model)
        
    def ask_to_model(self,input):
        response = self.__web_scraping(input)
        if response != "":
            print(response)
            return response
        for step in range(1):
            # encode the new user input, add the eos_token and return a tensor in Pytorch
            new_user_input_ids = self.tokenizer.encode(input + self.tokenizer.eos_token, return_tensors='pt')

            # append the new user input tokens to the chat history
            bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

            # generated a response while limiting the total chat history to 1000 tokens,
            chat_history_ids = self.model.generate(bot_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)

            response = self.tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response
    

    def __web_scraping(self,qs):
        global flag2
        global loading

        URL = 'https://www.google.com/search?q=' + qs
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')

        links = soup.findAll("a")
        all_links = []
        for link in links:
            link_href = link.get('href')
            if "url?q=" in link_href and not "webcache" in link_href:
                all_links.append((link.get('href').split("?q=")[1].split("&sa=U")[0]))

        flag = False
        for link in all_links:
            if 'https://en.wikipedia.org/wiki/' in link:
                wiki = link
                flag = True
                break

        div0 = soup.find_all('div', class_="kvKEAb")
        div1 = soup.find_all("div", class_="Ap5OSd")
        div2 = soup.find_all("div", class_="nGphre")
        div3 = soup.find_all("div", class_="BNeawe iBp4i AP7Wnd")

        if len(div0) != 0:
            return div0[0].text
        elif len(div1) != 0:
            return div1[0].text + "\n" + div1[0].find_next_sibling("div").text
        elif len(div2) != 0:
            return div2[0].find_next("span").text + "\n" + div2[0].find_next("div", class_="kCrYT").text
        elif len(div3) != 0:
            return div3[1].text
        elif flag == True:
            page2 = requests.get(wiki)
            soup = BeautifulSoup(page2.text, 'html.parser')
            title = soup.select("#firstHeading")[0].text

            paragraphs = soup.select("p")
            for para in paragraphs:
                if bool(para.text.strip()):
                    return title + "\n" + para.text
        return ""
    
    
        
        
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
            chat = LiteratureChats.query.filter_by(guid=chatId).first()
            messages = LiteratureMessage.query.filter_by(chatId=chat.guid).order_by(asc(LiteratureMessage.createDate)).all()
            context = {
            'chatId': chat.guid,
            'messages': messages
        }
        return render_template('chat_literature.html', **context)
    
    @staticmethod
    def send_message(chatId,data,fromWho):
        
        print(f"sql chatId : {chatId} && {chatId == 'None'}")
        
        if(chatId == "None" or chatId == '' or chatId == None):
            #create a new chat
            chat = LiteratureChats(userId=current_user.guid, chatName=data, deleted=0)
            db.session.add(chat)
            db.session.commit()
            chatId = chat.guid
            
        print(f"sql chatId : {chatId} && {chatId == 'None' }")
        print(f"sql data : {data}")
        
        message_from_user = LiteratureMessage(chatId=chatId,message=data,fromWho=fromWho)
        
        db.session.add(message_from_user)
        db.session.commit()
        
        return chatId