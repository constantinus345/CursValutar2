from distutils.command.config import config
import telegram
import requests
import configs
import json
import pymongo
import sys
from time import sleep
from bson.json_util import dumps
from DB_funcs import insert_df_data, read_sql_df
import pandas as pd
import os
from unidecode import unidecode as utf
from Telegram_funcs import Send_Telegram_Message

engine= configs.engine

#1 from txt to json
#every day, remove duplicate
#print(json.dumps(json_data, indent=4, sort_keys=True))

def distict_list_updateid (collection= configs.MongoT_Collection):
    """
    Returns a list of unique update_id
    """
    Mongo_client = pymongo.MongoClient(configs.MongoT_Client)
    Mongo_mydb = Mongo_client[configs.MongoT_Database]
    #Important: In MongoDB, a database is not created until it gets content!
    Mongo_mycol = Mongo_mydb[configs.MongoT_Collection]
    distinct_uid= Mongo_mycol.distinct('update_id')
    return distinct_uid

def Insert_Telegram_Interaction(conv):
    """
    inserts one integram interaction in Mongo
    """
    Mongo_client = pymongo.MongoClient(configs.MongoT_Client)
    Mongo_mydb = Mongo_client[configs.MongoT_Database]
    #Important: In MongoDB, a database is not created until it gets content!
    Mongo_mycol = Mongo_mydb[configs.MongoT_Collection]
    x = Mongo_mycol.insert_one(conv)


def insert_all_telegram_to_mongo(token= configs.Telegram_Token, collection= configs.MongoT_Collection):
    Report_TtoMongo = 0
    
    #'181414AAEuOPZ-enrrg4z5VVXDpPOxeQXJyLAfIvI'
    json_data= requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
    existing_updates= distict_list_updateid()
    for doc in json_data["result"]:
        if doc['update_id'] not in existing_updates:
            Insert_Telegram_Interaction(doc)
            Report_TtoMongo+= 1
            #print(f">>>Inserted update_id {doc['update_id']} in...{collection}")
        #else:
            #print(f"Update_id {doc['update_id']} already in...{collection}")
    if Report_TtoMongo>0:
        Send_Telegram_Message(configs.Telegram_Constantin, f"Inserted {Report_TtoMongo} telegram messages to Mongo")



def iterate_and_insert_postgres(token= configs.Telegram_Token, collection= configs.MongoT_Collection):
    Report_Mongo_Email_Postgres = 0
    Mongo_client = pymongo.MongoClient(configs.MongoT_Client)
    Mongo_mydb = Mongo_client[configs.MongoT_Database]
    #Important: In MongoDB, a database is not created until it gets content!
    Mongo_mycol = Mongo_mydb[configs.MongoT_Collection]

    qdistinct_updateid= """select distinct(updateid)
                        from mongo_telegram_text"""
    List_Updates_DB = read_sql_df(qdistinct_updateid)["updateid"].tolist()
    for document in Mongo_mycol.find():

        try:
            updateid= document["update_id"]
            userid= document["message"]["from"]["id"]
            message = document["message"]["text"]
        except:
            message=""

        if (message != "") and ("@" in str(message)) and (updateid not in List_Updates_DB):
            Cols_Mongo_Telegram_Text = configs.Cols_Mongo_Telegram_Text
            Data_Mongo_Telegram_Text = [updateid, userid,message]
            dictx= dict(zip(Cols_Mongo_Telegram_Text, Data_Mongo_Telegram_Text))
            dfx = pd.DataFrame(dictx, index=[0])
            #= ["updateid", "userid", "message"]
            insert_df_data(dfx, engine, configs.Table_Mongo_Text, if_exists="replace")
            Report_Mongo_Email_Postgres += 1
            print(f"Inserted {Data_Mongo_Telegram_Text}")

    if Report_Mongo_Email_Postgres > 0:
        Send_Telegram_Message(configs.Telegram_Constantin, f"Inserted {Report_Mongo_Email_Postgres} emails @-in-message to postgress")






def log_txt_folder(Folder= "E:/Dropbox/ONG Implicare Plus/OpSniperGov/Logs_Telegram"): 
    files= os.listdir(Folder)
    existing_updates= distict_list_updateid()
    os.chdir(Folder)
    for txt in files:
        print(txt)
        try:
            with open(txt, "r") as f:
                text = f.read().replace("'","\"").replace("False","false").replace("True","true").replace("/star","star")
                contents = json.loads(text)
                #text = utf(f.read()).replace("'","\"")
                #print(text[280:295])
                #text_json = json.loads(text)
                Insert_Telegram_Interaction(contents)
                print(f"Inserted {txt} to mongo")
        except Exception as e:
            print(e)





if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported mongo{sys.argv[0]}")


"""
docx =iterate_and_insert_postgres()
print(docx)
print(type(docx))
docx1= dumps(docx, indent=4)
print(docx1)
print(type(docx1))
docx2= json.loads(docx1)
print(type(docx2))
print("\n\n\n")
"""


