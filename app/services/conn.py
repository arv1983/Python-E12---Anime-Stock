import psycopg2
from environs import Env

env = Env()
env.read_env()



def conn_cur():
    conn = psycopg2.connect(host="localhost", database="anime", user="anderson", password="1234")

    cur = conn.cursor()

    return (
        conn,
        cur,
    )

def finalizar_conn_cur(conn, cur) -> None:
    conn.commit()
    cur.close()
    conn.close()