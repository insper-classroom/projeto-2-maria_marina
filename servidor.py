from flask import Flask
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from views import registrar_rotas

# Carrega as variáveis de ambiente do arquivo .cred
load_dotenv('.cred')

# Configurações para conexão com o banco de dados usando variáveis de ambiente
config = {
    'host': os.getenv('DB_HOST', 'localhost'),  # Obtém o host do banco de dados
    'user': os.getenv('DB_USER'),  # Obtém o usuário do banco de dados
    'password': os.getenv('DB_PASSWORD'),  # Obtém a senha do banco de dados
    'database': os.getenv('DB_NAME', 'defaultdb'),  # Obtém o nome do banco de dados
    'port': int(os.getenv('DB_PORT', 3306)),  # Obtém a porta do banco de dados
    'ssl_ca': os.getenv('SSL_CA_PATH')  # Caminho para o certificado SSL
}


# Função para conectar ao banco de dados
def connect_db():
    """Estabelece a conexão com o banco de dados usando as configurações fornecidas."""
    try:
        # Tenta estabelecer a conexão com o banco de dados usando mysql-connector-python
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as err:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro: {err}")
        return None


app = Flask(__name__)

registrar_rotas(app)

def registrar_rotas(app):

    @app.route("/imoveis", methods=["GET"])
    def listar_imoveis():
        from servidor import connect_db

        conn = connect_db()

        if conn is None:
            return {"erro": "Erro ao conectar ao banco de dados"}, 500

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM imoveis")
        resultados = cursor.fetchall()

        imoveis = []
        for imovel in resultados:
            imoveis.append({
                "id": imovel[0],
                "logradouro": imovel[1],
                "tipo_logradouro": imovel[2],
                "bairro": imovel[3],
                "cidade": imovel[4],
                "cep": imovel[5],
                "tipo": imovel[6],
                "valor": imovel[7],
                "data_aquisicao": imovel[8]
            })

        return {"imoveis": imoveis}, 200


    @app.route("/imoveis/<int:id>", methods=["GET"])
    def buscar_imovel(id):
        from servidor import connect_db

        conn = connect_db()

        if conn is None:
            return {"erro": "Erro ao conectar ao banco de dados"}, 500

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM imoveis WHERE id = %s", (id,))
        resultado = cursor.fetchone()

        if resultado is None:
            return {"erro": "Imóvel não encontrado"}, 404

        imovel = {
            "id": resultado[0],
            "logradouro": resultado[1],
            "tipo_logradouro": resultado[2],
            "bairro": resultado[3],
            "cidade": resultado[4],
            "cep": resultado[5],
            "tipo": resultado[6],
            "valor": resultado[7],
            "data_aquisicao": resultado[8]
        }

        return {"imovel": imovel}, 200

    
    @app.route("/imoveis", methods=["POST"])
    def add_novo_imovel():
        from servidor import connect_db

        conn = connect_db()
        if conn is None:
            return {"erro": "Erro ao conectar ao banco"}, 500

        dados = request.json
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

        return {"mensagem": "Imóvel adicionado com sucesso"}, 200
    
    @app.route("/imoveis/<int:id>", methods=["PUT"])
    def atualizar_imovel(id):
        from servidor import connect_db

        conn = connect_db()

        if conn is None:
            return {"erro": "Erro ao conectar ao banco de dados"}, 500

        dados = request.json

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
            return {"erro": "Imóvel não encontrado"}, 404

        return {"mensagem": "Imóvel atualizado com sucesso"}, 200
    
    @app.route("/imoveis/<int:id>", methods=["DELETE"])
    def delete_imovel(id):
        from servidor import connect_db

        conn = connect_db()

        if conn is None:
            return {"erro": "Erro ao conectar ao banco de dados"}, 500

        cursor = conn.cursor()

        sql = "DELETE from imoveis WHERE id=%s"
        valores = (id,)

        cursor.execute(sql, valores)
        conn.commit()

        if cursor.rowcount == 0:
            return {"erro": "Imóvel não encontrado"}, 404

        return {"mensagem": "Imóvel excluido com sucesso"}, 200
    
    @app.route("/imoveis/tipo/<string:tipo>", methods=["GET"])
    def listar_imoveis_por_tipo(tipo):
        from servidor import connect_db

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

        for imovel in resultados:
            imoveis.append({
                "id": imovel[0],
                "logradouro": imovel[1],
                "tipo_logradouro": imovel[2],
                "bairro": imovel[3],
                "cidade": imovel[4],
                "cep": imovel[5],
                "tipo": imovel[6],
                "valor": imovel[7],
                "data_aquisicao": imovel[8]
            })

        return {"imoveis": imoveis}, 200
    
    @app.route("/imoveis/cidade/<string:cidade>", methods=['GET'])
    def listar_imoveis_por_cidade(cidade):
        from servidor import connect_db

        conn = connect_db()

        if conn is None:
            return {"erro": "Erro ao conectar ao banco de dados"}, 500

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
        resultados = cursor.fetchall()

        imoveis = []

        for imovel in resultados:
            imoveis.append({
                "id": imovel[0],
                "logradouro": imovel[1],
                "tipo_logradouro": imovel[2],
                "bairro": imovel[3],
                "cidade": imovel[4],
                "cep": imovel[5],
                "tipo": imovel[6],
                "valor": imovel[7],
                "data_aquisicao": imovel[8]
            })

        return {"imoveis": imoveis}, 200