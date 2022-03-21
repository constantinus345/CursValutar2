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

os.chdir("D:/Python_Code/CursValutar2")

#print(generate_text_best_offer(tip = ["csv"], vorc = ["cump"], valuta= ["usd"]))

valute_lista= extract_cvtoday.valute_lista("banci")
valute_lista_str = extract_cvtoday.string_valute_descriptions(10,"banci")
print(valute_lista_str)

def getResponse(user_input):
    
    error_message_tryagain= f"""Întrebați robotul cel mai bun schimb valutar. Întrebarea Dvs trebuie să fie <b>exact 4 litere</b>, 
    prin care să ziceți dacă doriți să <b>cumpărați (c) sau să vindeți(v)</b>, și <b>codul standart valutei din 3 litere</b>. 
    De exemplu \ncEUR - doriți să cumpărați EURO,\n sau vRON - doriți să vindeți lei românești\n\n{valute_lista_str}""".replace("  ","")

    reply_str_negative=""
    reply_str_positive=""
    vorc_user , valuta_user = ["aa","ab"]
    if len(user_input)!=4:
        reply_str_negative= error_message_tryagain
    else:
        #validating vorc vinde or cumpara, plus INVERSING the values- bank buys customer sells an vversa
        if user_input.lower()[0] == "c":
            vorc_user = ["vanz"]
        elif user_input.lower()[0] == "v":
            vorc_user = ["cump"]
        else:
            reply_str_negative="""Prima literă poate fi c sau v: dacă doriți să cumpărați (c) sau să vindeți(v)""".replace("  ","")
        #validate currency
        if user_input.upper()[1:] in valute_lista:
            valuta_user= [user_input.upper()[1:]]
        else: 
            reply_str_negative= """Codul valutei (mereu de 3 litere) nu se află în lista de opțiuni"""

        if (vorc_user[0] in ["cump","vanz"]) and (valuta_user[0] in valute_lista):
            reply_str_positive_banca= extract_cvtoday.generate_text_best_offer(tip = ["banci"], 
                                        vorc = vorc_user, valuta= valuta_user)

            reply_str_positive = f"{reply_str_positive_banca}"
            """#Below includes from CSV
            reply_str_positive_csv= extract_cvtoday.generate_text_best_offer(tip = ["csv"], 
                                    vorc = vorc_user, valuta= valuta_user)
            #reply_str_positive = f"{reply_str_positive_banca}\n\n {reply_str_positive_csv}" 
            # """
        else: 
            if len(reply_str_negative)<10:
                reply_str_negative = error_message_tryagain

    if (vorc_user[0] in ["cump","vanz"]) and (valuta_user[0] in valute_lista):
        return reply_str_positive 
    else:
        return reply_str_negative

bot_link= f"https://api.telegram.org/bot{configs.Telegram_Key}/"

"""
import requests

img = open(your/local/image, 'rb')
TOKEN = 
CHAT_ID = 

url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={CHAT_ID}'


print(requests.post(url, files={'photo': img}))
"""


class MyHandler(http.server.SimpleHTTPRequestHandler):


    def do_POST(self):
    #try:
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
            user_input = json_data['message']['text']
        except:
            user_input = "notvalid"

        bot_output = getResponse(user_input)

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