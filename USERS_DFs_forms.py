from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame as DF
import configs
import pandas as pd
from sqlalchemy import create_engine
from unidecode import unidecode as deaccent
from time import time, sleep
from Other_Functions import Diff_Lists
from DB_funcs import remove_duplicates, insert_df_data, remove_duplicates_2cols
from Telegram_funcs import Send_Telegram_Message

drive_convoca_key = configs.drive_convoca_key
drive_buget_key = configs.drive_buget_key

enginex = configs.engine


def df_drive(spreadsheet_key, type_sheet):

    JSON_Creds="noble-aquifer-315512-90a1b2abaf1c.json"

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    #Reading Responses from https://forms.gle/YaViMoguTptoiaxY6
    credentials_drive = ServiceAccountCredentials.from_json_keyfile_name(JSON_Creds, scope) # Your json file here
    gc = authorize(credentials_drive)
    wks = gc.open_by_key(spreadsheet_key).get_worksheet(0)
    data = wks.get_all_values()
    headers = data.pop(0)
    df_User = DF(data, columns=headers)
    df_User.insert(0, "tip_subscription", type_sheet)
    len1= len(df_User)
    Cod_Col="Codurile localitatilor"
    df_User = df_User[df_User[Cod_Col]!='']
    len2 = len(df_User)

    if len1!= len2:
        Text_Rep = f"You have {len1-len2} missing codes for {type_sheet}"
        Send_Telegram_Message(configs.Telegram_Constantin, Text_Rep)

    return df_User

def Retrive_and_update_customers_sb():
    Report_Rows_Inserted = 0

    current_time = int(time()) #Unix epoch time
    df_convoca_drive = df_drive(drive_convoca_key, "sedinte")
    df_convoca_drive.to_excel(f"Forms_Customers/Convoca_{current_time}.xlsx")

    df_buget_drive = df_drive(drive_buget_key, "bugetul_meu")
    df_buget_drive.to_excel(f"Forms_Customers/Buget_{current_time}.xlsx")

    df_joined= pd.concat([df_convoca_drive,df_buget_drive])
    #print(df_joined.columns.tolist())
    df_joined.to_excel(f"Forms_Customers/Merged_sb_{current_time}.xlsx")
    #Change all columns names
    df_joined.set_axis(configs.Columns_Users_Registered_List, axis=1, inplace=True)
    """
    print(len(df_joined.columns))
    df_joined = pd.read_excel("Merged 3Apr.xlsx", engine="openpyxl")
    df_joined.set_axis(configs.Columns_Users_Registered_List, axis=1, inplace=True)

    #insert_df_data(df_joined, engine, configs.Table_Users_Registered, if_exists="replace")
    print(len(df_joined.columns))
    """

    for x1 in range(len(df_joined)):
        df1= df_joined.iloc[[x1]]
        #print(len(df1["apl_codes_string"].tolist()[0]))
        if len(df1["apl_codes_string"].tolist()[0]) < 5:
            Send_Telegram_Message(configs.Telegram_Constantin ,f"One new user without codes: {df1['email_address'].tolist()[0]}")
        
        if len(df1["email_address"].tolist()[0]) > 6:
            insert_df_data(df1, enginex, configs.Table_Users_Registered, if_exists="replace")
            Report_Rows_Inserted += 1
            #print(f"Inserted {x1} out of {len(df_joined)}")

    if Report_Rows_Inserted > 0:
        Send_Telegram_Message(configs.Telegram_Constantin, f"New subscribers inserted = {Report_Rows_Inserted} from drive to Postgres")

    remove_duplicates_2cols(enginex, configs.Table_Users_Registered, "timestamp", "email_address")
#remove_duplicates(engine, table, dupl_column)

#Create a DB with users from form






def rsal_sql_code(engine, apl_code, table= configs.Table_RSAL_Data, limit = 100):
    """
    Returns the last x=limit elements for given=apl_code APL
    """
    query_today_cv =f"""SELECT *
                        FROM public.{table} as rsal_data
                        WHERE cod_apl = {apl_code}
                        ORDER BY data_publ DESC LIMIT {limit}
                        """

    with engine.connect() as conn:
        df_code = pd.read_sql(query_today_cv, con=conn)

        return df_code

def return_last_by_keyword_list_urls(apl_code, keyword_regex, occurences=2, limit= 200):
    """
    Returns a list of the URLs of the last 3 documents by keyword in disp_denumire
    """


    #Due to accents ședința sedința etc, I'll select more items and do processing in df
    """SELECT disp_denumire, disp_domeniu, url_decizie
    FROM rsal_data as rsal_data
    WHERE disp_denumire LIKE '%%sedin%%'
    ORDER BY data_publ DESC LIMIT 200
    """
    query = f"""
            SELECT disp_denumire, disp_domeniu, url_decizie
            FROM rsal_data as rsal_data
            WHERE cod_apl = '{apl_code}'
            ORDER BY data_publ DESC LIMIT {limit}
            """

    with enginex.connect() as conn:
        df_code = pd.read_sql(query, con=conn)

    df_code["disp_denumire"] = [deaccent(x).replace("\n","") for x in df_code["disp_denumire"]]
    df_code = df_code[df_code["disp_denumire"].str.contains(keyword_regex, case=False)]

    df_code_occurences = df_code.head(occurences)

    urls_apl_filtered= df_code_occurences["url_decizie"].tolist()
    return urls_apl_filtered



def APL_and_Codes(engine=enginex):
    query=  """
            select distinct on (denumire_apl)
                denumire_apl, cod_apl
            from rsal_data
            """
    with engine.connect() as conn:
        df_apls = pd.read_sql(query, con=conn)

    df_apls = df_apls.astype(str)

    # sorting by first name
    df_apls.sort_values("denumire_apl", inplace = True)
 
    # dropping ALL duplicate values
    df_apls.drop_duplicates(subset ="denumire_apl", inplace = True)

    APL_List_all = df_apls["denumire_apl"].tolist()
    APL_Code_all = df_apls["cod_apl"].tolist()
    return {"APLs":APL_List_all, "Codes":APL_Code_all}

def report_announced(unixtimestamp ,user_name, apl_name, apl_code, user_email, url_doc, channel_type,channel_value):

    
    Columns_Users_Announced_List = ["unixtimestamp","user_name", "apl_name", "apl_code", "user_email",\
      "url_doc", "channel_type","channel_value"]
    Cols_Data_Announced = [[unixtimestamp], [user_name], [apl_name], [apl_code], [user_email],\
      [url_doc], [channel_type],[channel_value]]

    dictx= dict(zip(Columns_Users_Announced_List, Cols_Data_Announced))
    dfx = pd.DataFrame(dictx)

    return dfx




import sys
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")



