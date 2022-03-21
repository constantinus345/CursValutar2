#& d:/Python_Code/CursValutar2/Scripts/python.exe d:/Python_Code/CursValutar2/extract_list_banks.py

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

from random import randint as rdm
from time import sleep
import configs

import psycopg2
from sqlalchemy import create_engine

tip_2 = ["banci","csv"]



def get_list_institutii(tip):

    Curs_Banci_URL= f"https://www.curs.md/ro/lista_{tip}"
    Curs_Banci_Request = requests.get(Curs_Banci_URL).content
    Curs_Soup = bs(Curs_Banci_Request, "html.parser")

    Curs_Generic_URL = "https://www.curs.md"

    Curs_Banci_Links =  []

    for div in Curs_Soup.find_all("div", {"class":"bank_logo"}):
        link = div.find("a", href= True)
        if (link is None) or ("bnm" in link['href']):
            continue
        institution = link['href'].split("/")[-1]
        Curs_Banci_Links.append(f"{institution}")
        
    return Curs_Banci_Links

#def get_df_institutii(list_inst):

def get_df_institutii():
    column_names = ["tip", "cod_cursmd", "denumire","adress"]

    df_Inst = pd.DataFrame(columns = column_names)
    Curs_Banci_URL_generic = f"https://www.curs.md/ro/office"

    inst_count= 0
    for tip_x in tip_2:

        Inst_List= get_list_institutii(tip_x)

        for inst in Inst_List:
            print(f"Getting {tip_x} > {inst}")
            Row= []
            Row = [tip_x, inst] #structure column_names
            Curs_Banci_Request = requests.get(f"{Curs_Banci_URL_generic}/{inst}").content
            Curs_Soup = bs(Curs_Banci_Request, "html.parser")

            Inst_Name= Curs_Soup.select_one("#bankBox > div > div:nth-child(1) > h1").get_text()
            #bankBox > div > div:nth-child(4)
            Inst_Address = Curs_Soup.select_one("address").get_text().replace("\n","").replace("  ","")

            Row.extend([Inst_Name, Inst_Address])
            inst_count += 1
            print(Row)
            print(f"Processed > {inst_count} institutii\n{'_'*60}")
        
            df_Inst_len = len(df_Inst)

            df_Inst.loc[df_Inst_len] = Row

            sleep(rdm(1,3))
    return df_Inst
"""
print(df_Inst)
print(len(df_Inst))


Curs_Generic_URL = "https://www.curs.md"

Banci_List= get_list_institutii(tip_2[0])

CSV_List = get_list_institutii(tip_2[1])

print(f"Banci({len(Banci_List)}):\n{Banci_List}\n\n\n\nCSV({len(CSV_List)}):\n{CSV_List}")

print("Max code len= ",len(max([max(Banci_List, key= len), max(CSV_List, key= len)])))
    #print(div.get('href'))
"""

"""    for link in div.select("a.dev-link"):
        print link['href']"""

if __name__ == "__main__":
    try:
        
        Databasex="CursValutarDB".lower()
        Tablex="institutii".lower()
        engine = create_engine(f'postgresql://postgres:{configs.DB_password}@localhost:{configs.DB_port}/{Databasex}')
        df_Inst_all = get_df_institutii()
        print("got the df_Inst_all")
        df_Inst_all.to_sql(f'{Tablex}', engine, if_exists="append",index=False)
        print(f"Inserted df_Inst_all to SQL engine {Tablex}")
        engine.dispose()
    except Exception as ex:
        print(ex)

