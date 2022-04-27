#with engine.connect() as conn:

from email import header
from shutil import ignore_patterns
from pytz import timezone
from sqlalchemy import asc, create_engine
import configs
import pandas as pd
import datetime
import pause
import sys
from google_trans import translate_text

engine = create_engine(f"""postgresql://postgres:{configs.DB_password}\
@localhost:{configs.DB_port}/{configs.Database_CV}""")

    
def validate(date_text):
    try:
        if date_text != datetime.datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

#TODO if today returns empty list= not in DB, then return latest.

def extract_last_date_indb():
    Q_Last_Day = """select data_curs from public.exchange
    where data_curs = ( select max (data_curs) from  exchange )
    order by data_curs desc
    limit 1"""
    today_date= datetime.datetime.today()
    today_ymd = today_date.strftime("%Y-%m-%d")
    with engine.connect() as conn:
        df_last = pd.read_sql(Q_Last_Day, con=conn)
    last_day= df_last["data_curs"][0]
    if last_day!=today_ymd:
        print("DB Needs to be updated, Today!=LastDay_inDB")
    return last_day

def extract_df_today(date):
    """date can be a whatever string or value, gets validated as %Y-%m-%d"""
    if not validate(date):
        today_date= datetime.datetime.today()
        today_ymd = today_date.strftime("%Y-%m-%d")
        #print(validate(date))
        #print(today_ymd)
    else:
        today_ymd = date

    last_day_db= extract_last_date_indb()

    if today_ymd == last_day_db:
        date = today_ymd
    else: 
        date = last_day_db

    
    query_today_cv =f"""SELECT data_curs,tip,exdb.cod_cursmd, denumire, adress, valuta, valuta_nume, cump, vanz
                        FROM public.{configs.Table_Exchange} as exdb
                        left JOIN institutii on (exdb.cod_cursmd = public.{configs.Table_Inst}.cod_cursmd)
                        where data_curs = '{date}'
                        """
    with engine.connect() as conn:
        df_ex = pd.read_sql(query_today_cv, con=conn)

    df_ex = df_ex.drop_duplicates(ignore_index=False, keep="last")

    return df_ex #Might be a bug right here, I am not sure if the df is read continuously...


#df_today = extract_df_today(date="something- hence today")

def valute_lista(tip_institutie):

    today_date= datetime.datetime.today()
    today_ymd = today_date.strftime("%Y-%m-%d")
    Q2 =f"""
    SELECT valuta , valuta_nume, count(valuta) as freq
    FROM public.exchange as exdb
    left JOIN institutii on (exdb.cod_cursmd = public.institutii.cod_cursmd)
    where data_curs = '{today_ymd}' and tip = '{tip_institutie}'
    GROUP BY valuta, valuta_nume
    ORDER BY count(*) DESC;
    """
    with engine.connect() as conn:
        df_q2 = pd.read_sql(Q2, con=conn)
    
    Lista_Valutelor = df_q2["valuta"].tolist()
    return Lista_Valutelor

#print(valute_lista("banci"))

def string_valute_descriptions(amount, tip_institutie):
    today_date= datetime.datetime.today()
    today_ymd = today_date.strftime("%Y-%m-%d")
    tip_institutie = ['banci']
    Q2 =f"""
    SELECT valuta , valuta_nume, tip, count(valuta) as freq
    FROM public.exchange as exdb
    left JOIN institutii on (exdb.cod_cursmd = public.institutii.cod_cursmd)
    where data_curs = '{today_ymd}'
    GROUP BY valuta, valuta_nume, tip
    ORDER BY count(*) DESC;
    """

    with engine.connect() as conn:
        df_q2 = pd.read_sql(Q2, con=conn)
    
    df_q2 = df_q2[df_q2["tip"].isin(tip_institutie)]
    df_q2= df_q2.reset_index(drop=True)
    

    if len(df_q2) < amount:
        amount= len(df_q2)

    df_q2.iloc[:int(amount)] #mistake to put df_q2 = 

    df_q2 = pd.DataFrame.drop(df_q2,columns= ["freq","tip"])

    df_q2_str = ""
    for x in range(len(df_q2)):
        a= df_q2.loc[x, :].values.tolist()
        df_q2_str += f"{a[0]} = {a[1]}\n"

    #df_q2.reset_index(drop=True, inplace=False)

    #df_q2_str = pd.DataFrame.to_string(df_q2, columns=["valuta","valuta_nume"], header=False, col_space= 6, index= False)
    #this to_string didn't work... the above loop was made after to_string failed

    return df_q2_str

valute_listax= valute_lista("banci")
valute_lista_str = string_valute_descriptions(10,"banci")
print(valute_lista_str)
print(valute_listax)

#print(string_valute_descriptions(12))

def best_offer(tip, vorc, valuta, topx):
    """
    tip= banci or csv ; 
    vorc= cump or vanz; 
    valuta ABC
    returs Dataframe with topx biggest values 
    """

    dfx = extract_df_today("today")


    dfx_sort_colvalues =dfx.loc[(dfx["tip"].isin([x.lower() for x in tip])) 
                        & (dfx["valuta"].isin([y.upper() for y in valuta]))]

    #The bank is interested in the lowest cump price, the customer in largest
    #The bank is interested in the highest vanz price, the customer in smallest
    if "cump" in vorc:
        dfx_sort_topx = dfx_sort_colvalues.nlargest(topx, columns= vorc, keep="all").sort_values("cump", ascending=False)
    elif "vanz" in vorc:
        dfx_sort_topx = dfx_sort_colvalues.nsmallest(topx, columns= vorc, keep="all").sort_values("vanz", ascending=True)
    else:
        dfx_sort_topx=[]
    
    return dfx_sort_topx

"""df_best_topx = best_offer(tip = ["banci"], vorc = ["vanz"], valuta= ["RON"], topx= 1)
df_best_topx_cols = df_best_topx.columns.tolist()
print(df_best_topx_cols)
print(df_best_topx)"""



df_best = best_offer(["banci"], ["cump"], ["EUR"], 10)

def replace_bank_names(list_names):
    for x in range(len(list_names)):
        if "COMERŢBANK" in list_names[x]:
            list_names[x]= "COMERŢBANK"
        elif "ENERGBANK" in list_names[x]:
            list_names[x]= "ENERGBANK"
        elif "MAIB " in list_names[x]:
            list_names[x]= "MAIB "
        elif "Victoriabank" in list_names[x]:
            list_names[x]= "Victoriabank"
        elif "Banca Comercială Română" in list_names[x]:
            list_names[x]= "BCR"
        elif "EuroCreditBank" in list_names[x]:
            list_names[x]= "EuroCreditBank"
        elif "EXIMBANK" in list_names[x]:
            list_names[x]= "EXIMBANK"
        elif "FinComBank " in list_names[x]:
            list_names[x]= "FinComBank "
        elif "Moldindconbank" in list_names[x]:
            list_names[x]= "Moldindconbank"
        elif "OTP Bank" in list_names[x]:
            list_names[x]= "OTP Bank"
        else: 
            pass


    return list_names

def all_curs_str(tip, vorc, valuta, topx=10):

    df_best = best_offer(tip, vorc, valuta, topx)
    df_best = df_best[df_best["cump"].notna()]
    df_best = df_best[df_best["vanz"].notna()]
    Bank_Names = replace_bank_names(df_best["denumire"].tolist())
    Bank_Cump = df_best["cump"].tolist()
    Bank_Vanz = df_best["vanz"].tolist()
    #print(Bank_Names)
    max_len_name = max(Bank_Names, key= len)

    if "cump" in vorc:
        Bank_Offer = Bank_Cump
    else:
        Bank_Offer = Bank_Vanz
    
    #print(len(Bank_Names), len(Bank_Offer))
    str_offer = """"""
    for x in range(len(Bank_Names)):
        bank_len_name = len(Bank_Names[x])
        bank_name_diffmax = len(max_len_name) - bank_len_name
        offer = f"{Bank_Names[x]}{' '*bank_name_diffmax} = {round(int(Bank_Offer[x])/10000,3)}"
        str_offer += f"{offer}\n"

    return str_offer



def generate_top_text(tip, vorc, valuta, topx=1):
    today_date= datetime.datetime.today()
    today_ymd = today_date.strftime("%Y-%m-%d")
    Valuta= valuta[0]
    try:
        if vorc[0] == "cump":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de schimb")
            Text_ro = f"""<b>Dumneavoastră vindeți {Valuta},  \n\n{str_institutie_tip_oferta} cumpără {Valuta}, {today_ymd}:</b>"""
        elif vorc[0] == "vanz":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de Schimb")
            Text_ro = f"""<b>Dumneavoastră cumpărați {Valuta},  \n\n{str_institutie_tip_oferta} vinde {Valuta}, {today_ymd}:</b>"""
        else:
            str_institutie_tip_oferta= ""
    
    except Exception as err1:
        print(f"!!! Error = {err1}")

    return Text_ro

tip = ["banci"]
vorc = ["cump"]
valuta = ["EUR"]
topx = 10
#print(all_curs_str(tip,vorc, valuta))
#print(generate_top_text(tip, vorc, valuta))
#__________________________________________________________________


#TODO Vanzare cumparare String Formatting and other implications

if __name__ == "__main__":
    print(f"Executing the main {sys.argv[0]}")
    #print(generate_text_best_offer(tip = ["csv"], vorc = ["cump"], valuta= ["usd"]))
else: 
    print(f"Imported {sys.argv[0]}")

