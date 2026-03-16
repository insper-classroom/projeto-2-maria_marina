import sqlite3

def get_imoveis():
    conn = sqlite3.connect('imoveis.sql')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    resposta = cursor.execute("""
        SELECT * FROM imoveis
    """)
    print(resposta)

    rows = cursor.fetchall()
    conn.close()
    return rows

get_imoveis()