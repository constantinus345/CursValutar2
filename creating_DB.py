#& d:/Python_Code/CursValutar2/Scripts/python.exe d:/Python_Code/CursValutar2/creating_DB.py

import psycopg2
from sqlalchemy import create_engine
import configs 

Databasex="CursValutarDB".lower()
Tablex="institutii".lower()

Columnsx = """
tip VARCHAR(10),
cod_cursmd VARCHAR(30),
denumire VARCHAR(300),
adress VARCHAR(500)
"""

Table_Exchange = "Exchange".lower()
Columns_Exchange = """
data_curs Date,
cod_cursmd VARCHAR(30),
Valuta VARCHAR(5),
Valuta_nume VARCHAR(100),
Nominal int,
cump int,
vanz int,
tstamp timestamp
"""


try:
    conn = psycopg2.connect(
       database=Databasex, user= configs.DB_user , password= configs.DB_password , host= configs.DB_host, port= configs.DB_port
    )
    cur = conn.cursor()
    conn.close()
except Exception as e:
    print(e)
    conn = psycopg2.connect(
       database="postgres", user= configs.DB_user , password= configs.DB_password , host= configs.DB_host, port= configs.DB_port)
    
    cursor = conn.cursor()
    
    conn.autocommit = True
    sql = f'''CREATE database {Databasex}'''
    
    #Creating a database
    cursor.execute(sql)
    print("Database created successfully........")
    conn.commit()
    #Closing the connection
    conn.close()
#Creating a cursor object using the cursor() method

conn = psycopg2.connect(
   database=Databasex, user= configs.DB_user , password= configs.DB_password , host= configs.DB_host, port= configs.DB_port
)
cursor = conn.cursor()

engine = create_engine(f'postgresql://postgres:{configs.DB_password}@localhost:{configs.DB_port}/{Databasex}')


"""
Fetches all tables and if Tablex is not there, it creates it
Uses ColumnsX schema
"""

cursor.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
    
try:
   tables = [i[0] for i in cursor.fetchall()] # A list() of tables.
except:
   tables = []

def create_table(Table_name,Column_List):
   if Table_name.lower() not in tables:
      #Creating table as per requirement
      sql =f'''CREATE TABLE {Table_name}({Column_List});'''
      print(repr(sql))
      cursor.execute(sql)
      
      print(f"Table {Table_name} created successfully")
      conn.commit()
   else: 
      print(f"{Table_name} already exists")

create_table(Tablex, Columnsx)
create_table(Table_Exchange, Columns_Exchange)

conn.close()
engine.dispose()