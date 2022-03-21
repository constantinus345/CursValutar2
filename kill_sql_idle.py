#& d:/Python_Code/CursValutar/Scripts/python.exe d:/Python_Code/CursValutar/kill_sql_idle.py

import configs
from sqlalchemy import text, create_engine

def kill_sql_idle():
    Idle_Kill_Q = """
    SELECT
        pg_terminate_backend(pg_stat_activity.pid)
    FROM
        pg_stat_activity
    WHERE
        pg_stat_activity.datname = 'cursvalutardb'
        AND pid <> pg_backend_pid()
        AND state in ('idle');
    """

    engine = create_engine(f"""postgresql://postgres:{configs.DB_password}\
    @localhost:{configs.DB_port}/{configs.Database_CV}""".replace("    ",""))

    with engine.connect() as conn:
        conn.execute(text(Idle_Kill_Q))

if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")