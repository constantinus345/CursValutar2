import configs
import pandas as pd
import re
from PDFs_Download import list_from_urls_docs_str, download_pdf_rsal_list

enginex = configs.engine


with enginex.connect() as conn:
    print(conn)
    print(type(conn))

def insert_df_data(dfx, table, engine = enginex, if_exists="append"):
    with engine.connect() as conn:
        dfx.to_sql(f'{table}', con=conn, if_exists = if_exists, index=False)

def codesrsal (engine= enginex):
    with engine.connect() as conn:
        df_codes = pd.read_sql("SELECT * FROM public.codes", con=conn)
    list_codes = df_codes["cod"].tolist()
    return list_codes


def codes_users_unique (engine=enginex, table= configs.Table_Users_Registered):
    """
    Returns a list of users preferences as list of strings
    """
    with engine.connect() as conn:
        df_codes = pd.read_sql(f"SELECT * FROM {table}", con=conn)
    list_codes = df_codes["apl_codes_string"].tolist()
    
    return list_codes


def email_registered(table= configs.Table_Users_Registered, engine=enginex):
    """
    A list of emails registered
    """
    with engine.connect() as conn:
        df_codes = pd.read_sql(f"SELECT * FROM {table}", con=conn)
    user_emails = list(set(df_codes["email_address"].tolist()))
    
    return user_emails



def useremail_url_aplcod_check_channel_announcement(user_mail, url_rsal, aplcod, channel_type):
    """
    Returns if the combination (user_mail, url_rsal) exists= user was announced, bool
    """
    query= f"""SELECT * FROM public.users_announced 
    WHERE user_email = '{user_mail}'
        AND url_doc = '{url_rsal}'
        AND apl_code = '{aplcod}'
        AND channel_type = '{channel_type}'
        """
    with enginex.connect() as conn:
        df_codes = pd.read_sql(query, con=conn)

    if len(df_codes)>0 :
        exist = True
    else:
        exist = False
    return exist


    

def user_registered_dict(user_mail, table= configs.Table_Users_Registered, engine=enginex):
    """
    Returns dict with email_channel_topics_codes_registered
    """
    """table= configs.Table_Users_Registered
        user_mail = "constantin.copaceanu@gmail.com"""
    query = f"""SELECT *
            FROM {table}
            WHERE email_address = '{user_mail}' """
    
    with engine.connect() as conn:
        df_codes = pd.read_sql(query, con=conn)

    email = user_mail
    name = df_codes["user_fullname"].tolist()[0]
    channel = ",".join(df_codes["channels"].tolist())
    topics = ",".join( df_codes["topics"].tolist() )
    codes =  ",".join( df_codes["apl_codes_string"].tolist())
    #TODO extract phones by condition - starts with 373 and len=, starts with 6 or 7 and len=.
    #phone now as list
    try:
        phone = ",".join( df_codes["phone"].tolist())
    except TypeError:
        phone = "00"
    #print(phone)
    try:
        telegramid =  ",".join( str(x) for x in df_codes["telegram_user_id"].tolist())
        #returns the first integer from string
        telegramid = re.search(r'\d+', telegramid).group()
    except AttributeError:
        telegramid = 0


    dict_user = {"email":email, "name":name, "channel":channel,"topics":topics,\
         "codes":codes, "telegramid":telegramid, "phone":phone}
    return dict_user




def urls_announced (engine= enginex):
    """
    Returns a list of users preferences as list of strings
    """
    with engine.connect() as conn:
        df_codes = pd.read_sql("SELECT * FROM public.users_announced", con=conn)
    url_announced_list = list(set(df_codes["url_doc"].tolist()))
    return url_announced_list

def usersEmails_announced (engine= enginex):
    """
    Returns a list of users preferences as list of strings
    """
    with engine.connect() as conn:
        df_codes = pd.read_sql("SELECT * FROM public.users_announced", con=conn)
    usersEmails_announced = list(set(df_codes["user_email"].tolist()))
    return usersEmails_announced



def codes_users_unique (engine= enginex):
    with engine.connect() as conn:
        df_codes = pd.read_sql("SELECT * FROM public.users_registered", con=conn)
    list_codes = df_codes["apl_codes_string"].tolist()
    
    Coduri1=[]
    for cod in list_codes:
        cod = cod.replace(" ","")
        Coduri1.extend(cod.split(","))
    Coduri=list(set(Coduri1))

    Coduri = [x for x in Coduri if len(x)==5]
    return Coduri

def read_sql_df(sql_query, engine= enginex):
    with engine.connect() as conn:
        dfx = pd.read_sql(sql_query, con=conn)
    return dfx



def remove_duplicates(table, dupl_column, engine= enginex):
    sqlq= f"""
    DELETE FROM
    {table} a
        USING {table} b
    WHERE
    a.id < b.id
    AND a.{dupl_column} = b.{dupl_column};
    
    """
    with engine.connect() as conn:
        conn.execute(sqlq)



def remove_duplicates_2cols(table, dupl_column1, dupl_column2, engine= enginex):
    sqlq= f"""
    DELETE FROM
    {table} a
        USING {table} b
    WHERE
    a.id < b.id
    AND a.{dupl_column1} = b.{dupl_column1}
    AND a.{dupl_column2} = b.{dupl_column2};
    
    """
    with engine.connect() as conn:
        conn.execute(sqlq)

def existing_URLs_sql(apl_code, engine= enginex):
    sql_query = f"""
    SELECT url_decizie 
    FROM public.rsal_data 
    WHERE cod_apl = {apl_code}
    """
    
    with engine.connect() as conn:
        dfx = pd.read_sql(sql_query, con=conn)
    #Select url_decizie from public.rsal_data where cod_apl = 18515
    URLs= dfx["url_decizie"].tolist()
    return URLs
    

def data_rsal_from_url(urlx):
    sql_query = f"""
    SELECT *
    FROM rsal_data 
    WHERE url_decizie = '{urlx}'
    """
    with enginex.connect() as conn:
        dfx = pd.read_sql(sql_query, con=conn)

    disp_name = dfx["disp_denumire"].tolist()[0]
    data_disp = dfx["data_disp"].tolist()[0].strftime("%d-%b-%Y")
    try:
        pdfs_string = dfx["urls_docs_str"].tolist()[0]
        pdf_dw_list = download_pdf_rsal_list(pdfs_string)
    except Exception as e:
        print(f"PDF List error - {e}")
        pdf_dw_list=[]


    return {"disp_name":disp_name, "data_disp":data_disp, "pdf_dw_list":pdf_dw_list}




from sys import argv
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {argv[0]}")

