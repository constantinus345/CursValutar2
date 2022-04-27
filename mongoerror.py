from mongo_log_conversations import Insert_Telegram_Interaction as insert_mongo
import json

def json_processing(doc):
    doc= str(doc).replace("\'", "\"").replace("False","false").replace("True","true")
    #print(doc)
    json_data = json.loads(doc)
    insert_mongo(json_data)
    #insert_mongo(doc)

