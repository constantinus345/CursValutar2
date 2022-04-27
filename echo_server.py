#& d:/Python_Code/CursValutar2/Scripts/python.exe d:/Python_Code/CursValutar2/echo_server.py
#> d:/Python_Code/CursValutar/Server_Output.txt

"""
& d:/Python_Code/CursValutar/Scripts/python.exe d:/Python_Code/CursValutar/echo_server.py > d:/Python_Code/CursValutar/Server_Output.txt
"""

import socketserver
import http.server
import ssl
import json
import requests
import configs
from mongo_log_conversations import Insert_Telegram_Interaction as insert_mongo
import extract_cvtoday
import os
from getResponse import getResponse

os.chdir("D:/Python_Code/CursValutar2")
#print(generate_text_best_offer(tip = ["csv"], vorc = ["cump"], valuta= ["usd"]))

bot_link= f"https://api.telegram.org/bot{configs.Telegram_Key}/"

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
    #try:
        print("XINcoming")
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        json_data = json.loads(post_data)
        insert_mongo(json_data)
        try:
            chat_id = json_data['message']['from']['id']
        except:
            chat_id = 1307289323

        try:
            Person_fname = json_data['message']['from']['first_name']
            Person_text = json_data['message']['text']
            print(f"{Person_fname} searched {Person_text}")
        except:
            pass

        try:
            #Person_fname = json_data['message']['from']['first_name']
            Person_lang = json_data['message']['from']['language_code']
            #print(f"{Person_fname} searched {Person_text}, lang= {Person_lang}")
            print(Person_lang)
        except:
            Person_lang = "en"
            print("PNAME ERROR")

        try:
            user_input = json_data['message']['text']
        except:
            user_input = "notvalid"

        bot_output = getResponse(user_input, Person_lang)

        url= f"{bot_link}sendMessage"
        r= requests.post(url=url, params = {'chat_id':chat_id, 'text': bot_output, 'parse_mode': 'HTML'})


        if r.status_code == 200:
            self.send_response(200)
            self.end_headers()

        """
        url_image= f"{bot_link}sendPhoto"
        photo_path= ""
        r= requests.post(url=url, params = {'chat_id':chat_id, 'photo': img, parse_mode= 'HTML'}) ???
        """
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

server = socketserver.TCPServer(('0.0.0.0', 8443), MyHandler)
server.socket = ssl.wrap_socket(server.socket,
                                ca_certs= "SSL/ca_bundle.crt",
                                certfile= "SSL/certificate.crt",
                                keyfile= "SSL/private.key",
                                server_side= True)

server.serve_forever()