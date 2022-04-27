import extract_cvtoday
from google_trans import translate_text
import html


import datetime as dt  
def isNowInTimePeriod(startTime, endTime, nowTime): 
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime 


def getResponse(user_input, lang_response):
    valute_lista= extract_cvtoday.valute_lista("banci")
    valute_lista_str_ro = extract_cvtoday.string_valute_descriptions(10,"banci").replace("\n", " , ")
    #print(valute_lista_str)
    valute_lista_str = translate_text(target_language=lang_response, text= valute_lista_str_ro)
    valute_lista_str = html.unescape(valute_lista_str["translatedText"])


    error_message_tryagain_ro= f"""Întrebați robotul cel mai bun schimb valutar din Moldova. Întrebarea Dvs trebuie să fie <b>exact 4 litere</b>, 
    prin care să ziceți dacă doriți să <b>cumpărați (c) sau să vindeți(v)</b>, și <b>codul standart valutei din 3 litere</b>. 
    De exemplu \n<b>cEUR</b> - doriți să cumpărați EURO,\n sau <b>vRON</b> - doriți să vindeți lei românești. Răspunsul va fi în limba în care ați setat Telegram""".replace("  ","")

    error_message_tryagain = translate_text(target_language=lang_response, text= error_message_tryagain_ro)
    error_message_tryagain = html.unescape(error_message_tryagain["translatedText"])
    error_message_tryagain = f"{error_message_tryagain}\n\n{valute_lista_str}"
    #print(error_message_tryagain)

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
            reply_str_negative_ro="""Prima literă poate fi c sau v: dacă doriți să cumpărați (c) sau să vindeți(v)""".replace("  ","")
            reply_str_negative = translate_text(target_language=lang_response, text= reply_str_negative_ro)
            reply_str_negative = html.unescape(reply_str_negative["translatedText"])
        #validate currency
        if user_input.upper()[1:] in valute_lista:
            valuta_user= [user_input.upper()[1:]]
        else: 
            reply_str_negative_ro= f"""Codul valutei (mereu de 3 litere) nu se află în lista de opțiuni.\nBăncile au disponibil azi:"""
            reply_str_negative = translate_text(target_language=lang_response, text= reply_str_negative_ro)
            reply_str_negative = html.unescape(reply_str_negative["translatedText"])
            #\n<i><b>{valute_lista_str}</b></i>
            reply_str_negative = f"{reply_str_negative}\n\n{valute_lista_str}"
        if (vorc_user[0] in ["cump","vanz"]) and (valuta_user[0] in valute_lista):
            reply_str_positive_banca_ro = extract_cvtoday.generate_top_text(["banci"], vorc_user, valuta_user)
            reply_str_positive_banca = translate_text(target_language=lang_response, text= reply_str_positive_banca_ro)
            reply_str_positive_banca = html.unescape(reply_str_positive_banca["translatedText"])

            reply_str_positive = f"{reply_str_positive_banca}\n{extract_cvtoday.all_curs_str(['banci'], vorc_user, valuta_user)}"

        else: 
            if len(reply_str_negative)<10:
                reply_str_negative = error_message_tryagain


    if isNowInTimePeriod(dt.time(0,1), dt.time(8,59), dt.datetime.now().time()):
        reply_str_time_en= f"""Please try after 9:00AM"""
        reply_str_time = translate_text(target_language=lang_response, text= reply_str_time_en)
        reply_str_time = html.unescape(reply_str_time["translatedText"])
        return reply_str_time

    elif (vorc_user[0] in ["cump","vanz"]) and (valuta_user[0] in valute_lista):
        return reply_str_positive 
    else:
        return reply_str_negative




