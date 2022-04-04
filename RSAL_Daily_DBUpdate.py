#& d:/Python_Code/ActeLocale/Scripts/python.exe d:/Python_Code/ActeLocale/RSAL_Daily_DBUpdate.py

import pandas as pd
from time import sleep
from time import perf_counter as timing
from random import uniform as rdm
import configs
from sqlalchemy import create_engine
from Request_Functions import Request_RSAL, Dict_One_Doc,List_Hrefs_Codes
from DB_funcs import insert_df_data, codesrsal, existing_URLs_sql, remove_duplicates
from Other_Functions import Diff_Lists
from Telegram_funcs import Send_Telegram_Message

timing1= timing()

engine = configs.engine
codesrsal_list = codesrsal(engine)
#print(codesrsal_list)

#iDisplayLength= str(10)
iDisplayLength= str(100)
#apl_cod = str(18515) #Cioara
iDisplayStart = str(0)
#Loop all APL codes
total_reqs=0
print("Starting")

RSAL_Daily_Report = 0
#[::-1] for reversed
for apl_cod in codesrsal_list:
#for apl_cod in [19100]:
    
    Response1 = Request_RSAL(iDisplayLength,apl_cod,iDisplayStart)
    
    URLs_Response= List_Hrefs_Codes(Response1)
    URLs_SQL = existing_URLs_sql(engine=engine, apl_code=apl_cod)
    URLs_ToProcess = Diff_Lists(URLs_Response,URLs_SQL)
    
    print(f"{'_'*60}")
    print(f"{apl_cod}= {Response1['APL_total_docs']} TOTAL")
    print(f"{apl_cod}= {len(Response1['AData'])} REQESTED")
    print(f"{apl_cod}= {len(URLs_ToProcess)} TO PROCESS")
    print(f"{'_'*60}")


    for x in range(len(URLs_ToProcess)):
        Dict1 = Dict_One_Doc(URLs_ToProcess[x], apl_cod, x)
        dfx= pd.DataFrame.from_dict(Dict1)
        Name_APL= dfx["denumire_apl"][0]
        total_reqs +=1
        if total_reqs%20==0:
            print (f"Processed {total_reqs} requests ({x+1}/{len(URLs_ToProcess)} <{Name_APL}>)")

        with engine.connect() as conn:
            dfx.to_sql(f'{configs.Table_RSAL_Data}', con=conn, if_exists="append",index=False)
            RSAL_Daily_Report += 1
        sleep(round(rdm(0.02,0.05),2))
    sleep(round(rdm(0.1,0.3),2))

remove_duplicates(table= "rsal_data", dupl_column= "url_decizie",engine=engine)



timing2 = timing()
took= round(timing2-timing1, 2)
print(f"Took {took} secs")

if RSAL_Daily_Report> 0:
    Send_Telegram_Message(configs.Telegram_Constantin, f"Downloaded {RSAL_Daily_Report} rows/links from RSAL_daily.\nTook {took} seconds")