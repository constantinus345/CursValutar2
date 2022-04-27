#& d:/Python_Code/CursValutar2/Scripts/python.exe d:/Python_Code/CursValutar2/extract_curs_banks.py
import pandas as pd
import datetime
from time import sleep
import requests
from random import uniform as rdm
from time import sleep
import configs

import psycopg2
from sqlalchemy import create_engine


#2022-03-10
today_date = datetime.datetime.today()#.strftime("%Y-%m-%d")
today_date_str= today_date.strftime("%Y-%m-%d")
print(today_date_str)

days_historic = 1
#Generating a list of dates ranged in reverse
date_list = [today_date - datetime.timedelta(days=x) for x in range(days_historic)]
date_list = [x.strftime("%Y-%m-%d") for x in date_list]

print(f">{days_historic} days<")
#Reading the database table

Databasex="CursValutarDB".lower()
Table_Institutii="institutii".lower()
Table_Exchange = "Exchange".lower()

engine = create_engine(f'postgresql://postgres:{configs.DB_password}@localhost:{configs.DB_port}/{Databasex}')

with engine.connect() as conn:
    df_inst = pd.read_sql("SELECT * FROM public.institutii", con=conn)
insts_list = df_inst["cod_cursmd"].tolist()
#print(df_inst.columns)

with engine.connect() as conn:
    df_exchange = pd.read_sql("SELECT * FROM public.exchange", con=conn)

#This list will be used to avoid adding duplicates before requesting pd.read_html
Date_Inst_Exchange_Pairs_List = []

for x, y in zip(df_exchange["data_curs"].tolist(), df_exchange["cod_cursmd"].tolist()):

    Date_Inst_Exchange_Pairs_List.append([x,y])

df_exchange_columns_list = df_exchange.columns.tolist()

count_all= 0

ValueError_List = []
OtherErrors_List = []

Already_Exists = 0
for index_date, value_date in enumerate(date_list):
    for index_inst, value_inst in enumerate(insts_list):
        count_all +=1
        try:
            print(f"{'_'*60}\nReading {value_inst}/{value_date}")
            #if date and inst in db, skip, hence not reading twice
            if [value_date, value_inst] in Date_Inst_Exchange_Pairs_List:
                Already_Exists+=1
                print([value_date, value_inst])
                print("...already exists...")
                continue
            
            dfx= pd.read_html(f"https://www.curs.md/ro/office/{value_inst}/{value_date}/csv", attrs={'class': 'table table-hover'}, header=None)[0]
            print(f"{'_'*60}\nReading {value_inst}/{value_date}")


            dfx.insert(0, "cod_cursmd", value_inst)
            dfx.insert(0, "data_curs", value_date)
            dfx.insert(len(dfx.columns), "tstamp", datetime.datetime.now())

            dfx.columns = df_exchange_columns_list
            with engine.connect() as conn:
                dfx.to_sql(f'{Table_Exchange}', con=conn, if_exists="append",index=False)
            print(f"Inserted {df_inst['denumire'][index_inst]} {value_date} ({len(date_list)}days) to SQL engine {Table_Exchange}")

            
            print(f"Done {count_all} out of {len(date_list)*len(insts_list)}")
            sleep(rdm(0.2,2.5))
        except ValueError:
            ValueError_List.append([value_inst,value_date])
            print("ValueError - no table")

        except Exception as e:
            print(e)
            OtherErrors_List.append(e)

print(f"Loops= {count_all}")
print(f"Existing {Already_Exists} out of {count_all} occurences")
print(f"ValueError_List=\n{ValueError_List}")
print(f"\nOtherErrors_List=\n{OtherErrors_List}")


