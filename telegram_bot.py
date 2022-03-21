import json
import telegram
import configs
import datetime
import requests
import webbrowser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

#Get today
now = datetime.datetime.now()
Date_Time = now.strftime("%d-%m-%Y_%H:%M:%S")
print(Date_Time)
Hour= int(now.strftime("%H"))
#print(Hour)

bot = telegram.Bot(token=configs.Telegram_Key)
print(configs.Telegram_Link)
#bot.sendMessage(1307289323,"Aloha R1")

bot_link= f"https://api.telegram.org/bot{configs.Telegram_Key}/"
print("Updating JSON. How tf to do the webhooks?")
json_data= requests.get(f"{bot_link}getUpdates").json()

print(json_data)


kb = [[telegram.KeyboardButton('cEUR2')],
        [telegram.KeyboardButton('vUSD2')]]
kb_markup = telegram.ReplyKeyboardMarkup(kb)
bot.send_message(chat_id=1307289323,
                    text="Alegeti una din optiuni",
                    reply_markup=kb_markup)


bot.send_message(chat_id=1307289323,
                    text="R1",
                    reply_markup= ReplyKeyboardRemove(kb))

bot.sendMessage(1307289323, "whatever", InlineKeyboardButton("w2"))
bot.sendMessage(1307289323, "whatever", ReplyKeyboardRemove)

"""
#Setting the webhook
setWebhook = f"{bot_link}setWebhook?url={configs.Link_Web}:8443"
print(setWebhook)
webbrowser.open(setWebhook)"""

