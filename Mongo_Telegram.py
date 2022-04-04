import telegram
import requests
import configs
import json
import pymongo
import sys
from time import sleep
from bson.json_util import dumps
from DB_funcs import insert_df_data, engine, read_sql_df
import pandas as pd


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
    #'181414AAEuOPZ-enrrg4z5VVXDpPOxeQXJyLAfIvI'
    json_data= requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
    existing_updates= distict_list_updateid()
    for doc in json_data["result"]:
        if doc['update_id'] not in existing_updates:
            Insert_Telegram_Interaction(doc)
            #print(f">>>Inserted update_id {doc['update_id']} in...{collection}")
        #else:
            #print(f"Update_id {doc['update_id']} already in...{collection}")




def iterate_and_insert_postgres(token= configs.Telegram_Token, collection= configs.MongoT_Collection):
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
            print(f"Inserted {Data_Mongo_Telegram_Text}")


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


