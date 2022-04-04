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
from random import uniform as rdmf

bot = telegram.Bot(token= configs.Telegram_Token)

def Send_Telegram_Message(TelegramID, Text):
    bot.sendMessage(int(TelegramID), Text)
    sleep(round(rdmf(0.5,1.2),2))
    

def Send_Telegram_Attachments(TelegramID, List_Paths):
    for pdf in List_Paths:
    
        with open(pdf, "rb") as doc:
            bot.sendDocument(int(TelegramID),document=doc)
            sleep(round(rdmf(0.5,1.9),2))


