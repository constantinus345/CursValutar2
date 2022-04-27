import pymongo
import json
import configs
import sys

def Insert_Telegram_Interaction(conv):
    Mongo_client = pymongo.MongoClient(configs.MongoT_Client)
    Mongo_mydb = Mongo_client[configs.MongoT_Database]
    #Important: In MongoDB, a database is not created until it gets content!
    Mongo_mycol = Mongo_mydb[configs.MongoT_Collection]
    x = Mongo_mycol.insert_one(conv)

if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported mongo{sys.argv[0]}")