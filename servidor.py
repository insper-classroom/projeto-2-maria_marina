from flask import Flask, request, url_for
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv('.cred')

config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'defaultdb'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'ssl_ca': '/home/ubuntu/projeto-2-maria_marina/ca.pem'
}


def connect_db():
    """Estabelece a conexão com o banco de dados usando as configurações fornecidas."""
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as err:
        print(f"Erro: {err}")
        return None


app = Flask(__name__)

def mapear_imovel(linha):
    return {
        "id": linha[0],
        "logradouro": linha[1],
        "tipo_logradouro": linha[2],
        "bairro": linha[3],
        "cidade": linha[4],
        "cep": linha[5],
        "tipo": linha[6],
        "valor": linha[7],
        "data_aquisicao": linha[8]
    }

def adicionar_links_imovel(imovel):
    imovel["_links"] = {
        "self": url_for("buscar_imovel", id=imovel["id"]),
        "collection": url_for("listar_imoveis"),
        "update": url_for("atualizar_imovel", id=imovel["id"]),
        "delete": url_for("delete_imovel", id=imovel["id"])
    }
    return imovel

campos = [
    "logradouro", "tipo_logradouro", "bairro",
    "cidade", "cep", "tipo", "valor", "data_aquisicao"
]

@app.route("/imoveis", methods=["GET"])
def listar_imoveis():

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis")
    resultados = cursor.fetchall()

    imoveis = []
    for linha in resultados:
        imovel = mapear_imovel(linha)
        imoveis.append(adicionar_links_imovel(imovel))

    cursor.close()
    conn.close()

    return {
        "imoveis": imoveis,
        "_links": {
            "self": url_for("listar_imoveis"),
            "create": url_for("add_novo_imovel")
        }
    }, 200

@app.route("/imoveis/<int:id>", methods=["GET"])
def buscar_imovel(id):

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    if resultado is None:
        return {"erro": "Imóvel não encontrado"}, 404

    imovel = mapear_imovel(resultado)
    imovel = adicionar_links_imovel(imovel)

    return {"imovel": imovel}, 200


@app.route("/imoveis", methods=["POST"])
def add_novo_imovel():

    conn = connect_db()
    if conn is None:
        return {"erro": "Erro ao conectar ao banco"}, 500

    dados = request.json
    if not dados or not all(campo in dados for campo in campos):
        return {"erro": "Dados inválidos"}, 400
    cursor = conn.cursor()

    sql = """
    INSERT INTO imoveis (
        logradouro, tipo_logradouro, bairro, cidade,
        cep, tipo, valor, data_aquisicao
    ) VALUES ( %s, %s , %s, %s, %s, %s, %s, %s)
    """

    valores = (
        dados["logradouro"],
        dados["tipo_logradouro"],
        dados["bairro"],
        dados["cidade"],
        dados["cep"],
        dados["tipo"],
        dados["valor"],
        dados["data_aquisicao"]
    )

    cursor.execute(sql, valores)
    conn.commit()

    novo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    novo_imovel = {
        "id": novo_id,
        **dados
    }

    novo_imovel = adicionar_links_imovel(novo_imovel)

    return {"imovel": novo_imovel}, 201, {
        "Location": url_for("buscar_imovel", id=novo_id, _external=True)
    }

@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    dados = request.json
    if not dados or not all(campo in dados for campo in campos):
        return {"erro": "Dados inválidos"}, 400

    cursor = conn.cursor()

    sql = """
    UPDATE imoveis
    SET logradouro=%s, tipo_logradouro=%s, bairro=%s, cidade=%s,
        cep=%s, tipo=%s, valor=%s, data_aquisicao=%s
    WHERE id=%s
    """

    valores = (
        dados["logradouro"],
        dados["tipo_logradouro"],
        dados["bairro"],
        dados["cidade"],
        dados["cep"],
        dados["tipo"],
        dados["valor"],
        dados["data_aquisicao"],
        id
    )

    cursor.execute(sql, valores)

    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return {"erro": "Imóvel não encontrado"}, 404

    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
    resultado = cursor.fetchone()

    imovel = mapear_imovel(resultado)
    imovel = adicionar_links_imovel(imovel)

    cursor.close()
    conn.close()
    return {"imovel": imovel}, 200

@app.route("/imoveis/<int:id>", methods=["DELETE"])
def delete_imovel(id):

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    cursor = conn.cursor()

    sql = "DELETE from imoveis WHERE id=%s"
    valores = (id,)

    cursor.execute(sql, valores)
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return {"erro": "Imóvel não encontrado"}, 404

    cursor.close()
    conn.close()
    return '', 204

@app.route("/imoveis/tipo/<string:tipo>", methods=["GET"])
def listar_imoveis_por_tipo(tipo):

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM imoveis WHERE tipo = %s",
        (tipo,)
    )

    resultados = cursor.fetchall()

    imoveis = []

    for linha in resultados:
        imovel = mapear_imovel(linha)
        imoveis.append(adicionar_links_imovel(imovel))

    cursor.close()
    conn.close()

    return {
        "imoveis": imoveis,
        "_links": {
            "self": url_for("listar_imoveis_por_tipo", tipo=tipo),
            "collection": url_for("listar_imoveis")
        }
    }, 200

@app.route("/imoveis/cidade/<string:cidade>", methods=['GET'])
def listar_imoveis_por_cidade(cidade):

    conn = connect_db()

    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
    resultados = cursor.fetchall()

    imoveis = []

    for linha in resultados:
        imovel = mapear_imovel(linha)
        imoveis.append(adicionar_links_imovel(imovel))

    cursor.close()
    conn.close()

    return {
        "imoveis": imoveis,
        "_links": {
            "self": url_for("listar_imoveis_por_cidade", cidade=cidade),
            "collection": url_for("listar_imoveis")
        }
    }, 200

from unittest.mock import patch, MagicMock

@patch("servidor.connect_db")
def test_listar_imoveis_por_cidade_inexistente(mock_connect_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_connect_db.return_value = mock_conn

    response = client.get("/imoveis/cidade/São Paulo")

    assert response.status_code == 200

    data = response.get_json()
    assert "imoveis" in data
    assert data["imoveis"] == []