#with engine.connect() as conn:

from email import header
from shutil import ignore_patterns
from pytz import timezone
from sqlalchemy import create_engine
import configs
import pandas as pd
import datetime
import pause
import sys


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
    last_day= df_last["data_curs"][0].strftime("%Y-%m-%d")
    if last_day!=today_ymd:
        print("DB Needs to be updated, Today!=LastDay_inDB")
        
    return last_day


def extract_df_today(date):
    """date can be a whatever string or value, gets validated as %Y-%m-%d"""
    if not validate(date):
        today_date= datetime.datetime.today()
        today_ymd = today_date.strftime("%Y-%m-%d")

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

    df_ex = df_ex.drop_duplicates(ignore_index=True)

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
        dfx_sort_topx = dfx_sort_colvalues.nlargest(topx, columns= vorc, keep="all")
    elif "vanz" in vorc:
        dfx_sort_topx = dfx_sort_colvalues.nsmallest(topx, columns= vorc, keep="all")
    else:
        dfx_sort_topx=[]
    
    return dfx_sort_topx

"""df_best_topx = best_offer(tip = ["banci"], vorc = ["vanz"], valuta= ["RON"], topx= 1)
df_best_topx_cols = df_best_topx.columns.tolist()
print(df_best_topx_cols)

print(df_best_topx)"""

#TODO Vanzare cumparare String Formatting and other implications

def best_first_offer_dict(tip, vorc, valuta, topx=1):
    """
    tip= banci or csv ; 
    vorc= cump or vanz; 
    valuta ABC
    returs Dataframe with topx biggest values 
    """


    dfx_topx = best_offer(tip, vorc, valuta, topx)
    
    offer_dic = best_offer(tip, vorc, valuta, topx).to_dict(orient="list")
    #tip replace?
    return offer_dic

def generate_text_best_offer(tip, vorc, valuta, topx=1):

    best_dic= best_first_offer_dict(tip, vorc, valuta, topx=1)
    #print(best_dic)


    try:
        if vorc[0] == "cump":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de schimb")
            str_oferta_float = int(best_dic['cump'][0])/10000
            str_oferta = f"""{str_institutie_tip_oferta} cumpără {valuta[0].upper()} cu {str_oferta_float}
            \n(Dvs. vindeți {valuta[0].upper()})""".replace("  ","")
        elif vorc[0] == "vanz":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de Schimb")
            str_oferta_float = int(best_dic['vanz'][0])/10000
            str_oferta = f"""{str_institutie_tip_oferta} vinde {valuta[0].upper()} cu {str_oferta_float}
            \n(Dvs. cumpărați {valuta[0].upper()})""".replace("  ","")
        else:
            str_oferta= ""
    except Exception as err1:
        str_oferta= ""
        print(f"!!! Error = {err1}")

    str_institutie_tip = tip[0].replace("banci","bancă").replace("csv","casă de schimb valutar")
    str_operatiune = vorc[0].replace("vanz", "vânzare").replace("cump", "cumpărare")
    #Maybe change str_operatiune to opposite, given bank selling= customer buying? Confusing
    str_valuta = valuta[0].upper()
    try:
        str_date = best_dic["data_curs"][0].strftime('%d-%b-%Y')
    except:
        str_date = datetime.datetime.now().strftime('%d-%b-%Y')

    nr_institutii= len(best_dic["cump"])

    if nr_institutii == 1:
        reply_best = f"""Cel mai bun curs valutar pentru Dumneavostră:
        tipul instituției : {str_institutie_tip}
        data : {str_date}
        valuta : {str_valuta}
        este la {best_dic["denumire"][0]} ({str_institutie_tip})
        {str_oferta}
            """.replace("  ","")


    elif nr_institutii >1:
        str_denumiri= f"({nr_institutii} instituții):"
        for index_denumire, val in enumerate(best_dic["denumire"]):
            str_denumiri += f"\n{val}"
        
        reply_best = f"""Cel mai bun curs valutar pentru Dumneavostră::
        tipul instituției : {str_institutie_tip}
        data : {str_date}
        valuta : {str_valuta}
        {str_denumiri}
        {str_oferta}
            """.replace("  ","")

    else: 
        reply_best= ""
    return reply_best

if __name__ == "__main__":
    print(f"Executing the main {sys.argv[0]}")
    #print(generate_text_best_offer(tip = ["csv"], vorc = ["cump"], valuta= ["usd"]))
else: 
    print(f"Imported {sys.argv[0]}")

