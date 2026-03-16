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