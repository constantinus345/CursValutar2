import requests
import json
from bs4 import BeautifulSoup as bs
import Request_construct_1
import pandas as pd
from time import sleep
from random import randint as rdm
import configs
import datetime

def Request_RSAL(iDisplayLength, apl_cod,iDisplayStart='0', release_date_from='', release_date_to=''):

    resp1 = requests.post('https://actelocale.gov.md/ral/search/search_request', \
        headers= Request_construct_1.headerx(),\
             cookies= Request_construct_1.cookiex(), \
                 data= Request_construct_1.datax(iDisplayLength,apl_cod,iDisplayStart) )
    APL_total_docs= resp1.json()["iTotalRecords"]
    AData= resp1.json()["aaData"]
    return {"AData":AData,"APL_total_docs":APL_total_docs}


def List_Hrefs_Codes (resp_server):
    List_Hrefs = []
    Len_Adata = len(resp_server["AData"])
    for xdoc in range(Len_Adata):
        data_list= resp_server["AData"][xdoc][0]
        soup = bs(data_list, 'html.parser')
        div_doc = soup.find("div", {"class": "document_item"})
        div_doc_doc = div_doc.find("h5").find("a")
        #print(div_doc_doc.get('href'))
        URL_Decizie= div_doc_doc.get('href')
        List_Hrefs.append(URL_Decizie)
    return List_Hrefs


def URL_atrequest_index (resp_server, xdoc):
    data_list= resp_server["AData"][xdoc][0]
    #print(len(data_list))
    #print(type(data_list))
    #print("\n\n")
    soup = bs(data_list, 'html.parser')
    div_doc = soup.find("div", {"class": "document_item"})

    div_doc_doc = div_doc.find("h5").find("a")

    URL_Decizie= div_doc_doc.get('href')
    return URL_Decizie

def change_date_format(datex):
    date_sql= datetime.datetime.strptime(datex, '%d.%m.%Y').strftime('%Y-%m-%d')
    return date_sql

def Dict_One_Doc (URL_Decizie, apl_cod, xdoc):
    req_href= requests.get(URL_Decizie)
    soup2= bs(req_href.text, "html.parser")

    Disp_Links= []
    for a in soup2.find("div", {"class": "row m-0 p-0"}).find_all('a', href=True):

        if "ral/act/downloadAct/" in str(a['href']):
            Disp_Links.append(a['href'].split("/")[-1])

    URLs_docs_str = ";".join(Disp_Links)
    Data_Disp = soup2.find("div", {"class": "col-md-10 col-sm-9 p-0"})\
        .find("h4").get_text()[-10:]

    Disp_Denumire = soup2.find("div", {"class": "col-md-10 col-sm-9 p-0"})\
        .find("h1").get_text()

    Data_Publ = soup2.find("span", {"class": "data"}).get_text()

    Denumire_APL = soup2.find("div", {"class": "col-md-8 titlul_org"})\
        .find("p").get_text()

    try:
        Disp_Domeniu = soup2.find("div", {"class": "col-md-6 col-sm-12 font16 p-0"})\
            .find("b").get_text()
        #print(">>",Disp_Domeniu)
    except:
        Disp_Domeniu=""
    
    try:
        Disp_datepers = soup2.find("div", {"class": "col-md-6 col-sm-12 tr p-0 font16 has_personal_info"}).\
            find("b").get_text()
    except:
        Disp_datepers=""

    Disp_Data_date_oarecare = soup2.find("div", {"class": "date_oarecare tr"}).find("p")
    Disp_Data_date_oarecare = Disp_Data_date_oarecare.get_text().\
        replace("\n","").replace("ID intern unic:","").replace(" ","").replace("Vizualizari","")

    Disp_ID_intern= Disp_Data_date_oarecare.split(":")[0]
    Disp_vizualizari= Disp_Data_date_oarecare.split(":")[1]

    Cols_v= [[apl_cod], [Denumire_APL],[URL_Decizie], [URLs_docs_str],\
        [change_date_format(Data_Disp)], [Disp_Denumire], [change_date_format(Data_Publ)],\
            [Disp_Domeniu],[Disp_datepers],[Disp_ID_intern],[Disp_vizualizari]]
    Cols_n= configs.Cols_n

    Dict_Data = dict(zip(Cols_n,Cols_v))

    return Dict_Data

import sys
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")