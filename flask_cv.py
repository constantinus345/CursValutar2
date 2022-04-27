#cd "D:\Python_Code\WDreportt" ; Scripts\activate
#& d:/Python_Code/CursValutar2/Scripts/python.exe d:/Python_Code/CursValutar2/flask_cv.py

from flask import Flask,request,json
import configs
import requests
from getResponse import getResponse
from mongo_log_conversations import Insert_Telegram_Interaction as insert_mongo
import sys
from mongoerror import json_processing


app = Flask(__name__)

bot_link= f"http://api.telegram.org/bot{configs.Telegram_Key}/"
url= f"{bot_link}sendMessage"

@app.route('/')
def hello():
    return 'Webhooks with Python- Report MD.'

@app.route('/',methods=['POST', 'GET'])
def cvpost():
    try:
        json_data = request.json
        print(type(json_data))
        print(json_data)
        json_processing((json_data))
    except:
        print("Some error on reading data")
    
    try:
        #Person_fname = json_data['message']['from']['first_name']
        Person_lang = json_data['message']['from']['language_code']
        #print(f"{Person_fname} searched {Person_text}, lang= {Person_lang}")
        print(Person_lang)
    except:
        Person_lang = "en"
        print("PNAME ERROR")

    try:
        Person_fname = json_data['message']['from']['first_name']
        Person_text = json_data['message']['text']
        print(f"{Person_fname} searched {Person_text}")
    except:
        pass


    try:
        user_input = json_data['message']['text']
    except:
        user_input = "notvalid"

    try:
        Telegram_ID = json_data['message']['from']['id']
    except:
        print("chat_id")
        Telegram_ID = 1307289323

    bot_output = getResponse(user_input=user_input, lang_response= Person_lang)
    
    print(bot_output)#print(bot_output)
    #print(user_input)
    try:
        r= requests.post(url=url, params = {'chat_id':Telegram_ID, 'text': bot_output, 'parse_mode': 'HTML'})
    except:
        r= requests.post(url=url, params = {'chat_id':Telegram_ID, 'text': "errorx", 'parse_mode': 'HTML'})
    
    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=443, ssl_context="adhoc")#, ssl_context="adhoc"