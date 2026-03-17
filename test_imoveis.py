import pytest
from unittest.mock import patch, MagicMock
from servidor import app

@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("servidor.connect_db")
def test_get_imoveis(mock_connect_db, client):
    """Testa a rota GET /imoveis."""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, "Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
        (2, "Price Prairie", "Travessa", "Colonton", "North Garyville", "93354", "casa em condominio", 260069.89, "2021-11-30"),
        (3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24"),
    ]
    mock_connect_db.return_value = mock_conn

    # When
    response = client.get("/imoveis")
    # Then
    assert response.status_code == 200

    expected_response = {
        "imoveis": [
            {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"},
            {"id": 2, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep": "93354", "tipo": "casa em condominio", "valor": 260069.89, "data_aquisicao": "2021-11-30"},
            {"id": 3, "logradouro": "Taylor Ranch", "tipo_logradouro": "Avenida", "bairro": "West Jennashire", "cidade": "Katherinefurt", "cep": "51116", "tipo": "apartamento", "valor": 815969.92, "data_aquisicao": "2020-04-24"},
        ]
    }

    assert response.get_json() == expected_response
    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")


@patch("servidor.connect_db")
def test_buscar_imovel_por_id_existente(mock_connect_db, client):
    """
    Testa a rota GET /imoveis/<id> quando o imóvel existe.
    """

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (
        1,
        "Nicole Common",
        "Travessa",
        "Lake Danielle",
        "Judymouth",
        "85184",
        "casa em condominio",
        488423.52,
        "2017-07-29"
    )

    mock_connect_db.return_value = mock_conn
    # When
    response = client.get("/imoveis/1")
    # Then

    assert response.status_code == 200
    expected_response = {
        "imovel": {
            "id": 1,
            "logradouro": "Nicole Common",
            "tipo_logradouro": "Travessa",
            "bairro": "Lake Danielle",
            "cidade": "Judymouth",
            "cep": "85184",
            "tipo": "casa em condominio",
            "valor": 488423.52,
            "data_aquisicao": "2017-07-29"
        }
    }
    assert response.get_json() == expected_response

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (1,)
    )


@patch("servidor.connect_db")
def test_buscar_imovel_por_id_inexistente(mock_connect_db, client):
    """
    Testa a rota GET /imoveis/<id> quando o imóvel NÃO existe.
    """

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_connect_db.return_value = mock_conn
    # When
    response = client.get("/imoveis/9999")
    # Then

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (9999,)
    )


# dados padronizados usados nos testes
dados_imovel_teste = {
    "logradouro": "Nicole Common",
    "tipo_logradouro": "Travessa",
    "bairro": "Lake Danielle",
    "cidade": "Judymouth",
    "cep": "85184",
    "tipo": "casa em condominio",
    "valor": 500000,
    "data_aquisicao": "2024-01-01"
}

@patch("servidor.connect_db")
def test_add_novo_imovel(mock_connect_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    #when
    response = client.post("/imoveis", json=dados_imovel_teste)

    # Then
    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel adicionado com sucesso"}

    mock_cursor.execute.assert_called_once_with(
         """
        INSERT INTO imoveis (
            logradouro, tipo_logradouro, bairro, cidade,
            cep, tipo, valor, data_aquisicao
        ) VALUES ( %s, %s , %s, %s, %s, %s, %s, %s)
        """,
        (dados_imovel_teste["logradouro"],
            dados_imovel_teste["tipo_logradouro"],
            dados_imovel_teste["bairro"],
            dados_imovel_teste["cidade"],
            dados_imovel_teste["cep"],
            dados_imovel_teste["tipo"],
            dados_imovel_teste["valor"],
            dados_imovel_teste["data_aquisicao"])
        )
    
    mock_conn.commit.assert_called_once()


@patch("servidor.connect_db")
def test_atualizar_imovel_existente(mock_connect_db, client):
    """Testa atualizar um imóvel existente"""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1
    mock_connect_db.return_value = mock_conn

    # When
    response = client.put("/imoveis/1", json=dados_imovel_teste)

    # Then
    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        """
        UPDATE imoveis
        SET logradouro=%s, tipo_logradouro=%s, bairro=%s, cidade=%s,
            cep=%s, tipo=%s, valor=%s, data_aquisicao=%s
        WHERE id=%s
        """,
        (
            dados_imovel_teste["logradouro"],
            dados_imovel_teste["tipo_logradouro"],
            dados_imovel_teste["bairro"],
            dados_imovel_teste["cidade"],
            dados_imovel_teste["cep"],
            dados_imovel_teste["tipo"],
            dados_imovel_teste["valor"],
            dados_imovel_teste["data_aquisicao"],
            1
        )
    )

    mock_conn.commit.assert_called_once()


@patch("servidor.connect_db")
def test_atualizar_imovel_inexistente(mock_connect_db, client):
    """Testa atualizar um imóvel inexistente"""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0

    mock_connect_db.return_value = mock_conn

    # When
    response = client.put("/imoveis/999", json=dados_imovel_teste)

    # Then
    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("servidor.connect_db")
def test_delete_imovel(mock_connect_db, client):
    """"Testa a exclusão de um imóvel inexistente"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1
    mock_connect_db.return_value = mock_conn

    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel excluido com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE from imoveis WHERE id=%s",
        (1,)
    )

    mock_conn.commit.assert_called_once()

@patch("servidor.connect_db")
def test_delete_imovel_inexistente(mock_connect_db, client):

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0

    mock_connect_db.return_value = mock_conn

    # When
    response = client.delete("/imoveis/999", json=dados_imovel_teste)

    # Then
    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

@patch("servidor.connect_db")
def test_listar_imoveis_por_tipo(mock_connect_db, client):
    """Testa listar imoveis por tipo"""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24"),
        (4, "Green Street", "Rua", "Centro", "São Paulo", "01000", "apartamento", 400000, "2019-10-10"),
    ]
    mock_connect_db.return_value = mock_conn

    # When
    response = client.get("/imoveis/tipo/apartamento")

    # Then
    assert response.status_code == 200
    expected = {
        "imoveis": [
            {"id": 3, "logradouro": "Taylor Ranch", "tipo_logradouro": "Avenida", "bairro": "West Jennashire", "cidade": "Katherinefurt", "cep": "51116", "tipo": "apartamento", "valor": 815969.92, "data_aquisicao": "2020-04-24"},
            {"id": 4, "logradouro": "Green Street", "tipo_logradouro": "Rua", "bairro": "Centro", "cidade": "São Paulo", "cep": "01000", "tipo": "apartamento", "valor": 400000, "data_aquisicao": "2019-10-10"},
        ]
    }

    assert response.get_json() == expected
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s", ("apartamento",)
    )


@patch("servidor.connect_db")
def test_listar_imoveis_por_tipo_sem_resultados(mock_connect_db, client):
    """Testa listar imoveis por tipo sem resultado"""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    mock_connect_db.return_value = mock_conn

    # When
    response = client.get("/imoveis/tipo/castelo")

    # Then
    assert response.status_code == 200
    assert response.get_json() == {"imoveis": []}

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s", ("castelo",)
    )

@patch("servidor.connect_db")
def test_listar_imoveis_erro_conexao(mock_connect_db, client):
    """Testa erro de conexão ao listar imóveis"""

    # Given
    mock_connect_db.return_value = None

    # When
    response = client.get("/imoveis")

    # Then
    assert response.status_code == 500
    assert response.get_json() == {"erro": "Erro ao conectar ao banco de dados"}


@patch("servidor.connect_db")
def test_listar_imoveis_por_cidade(mock_connect_db, client):
    
    """Testa listar imoveis por cidade"""

    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (3, "Taylor Ranch", "Avenida", "West Jennashire", "São Paulo", "51116", "apartamento", 815969.92, "2020-04-24"),
        (4, "Green Street", "Rua", "Centro", "São Paulo", "01000", "apartamento", 400000, "2019-10-10"),
        (5, "Green Street", "Rua", "Centro", "Bentleymouth", "01000", "apartamento", 400000, "2019-10-10"),
    ]
    mock_connect_db.return_value = mock_conn

    # When
    response = client.get("/imoveis/cidade/São Paulo")

    # Then
    assert response.status_code == 200
    expected = {
        "imoveis": [
            {"id": 3, "logradouro": "Taylor Ranch", "tipo_logradouro": "Avenida", "bairro": "West Jennashire", "cidade": "São Paulo", "cep": "51116", "tipo": "apartamento", "valor": 815969.92, "data_aquisicao": "2020-04-24"},
            {"id": 4, "logradouro": "Green Street", "tipo_logradouro": "Rua", "bairro": "Centro", "cidade": "São Paulo", "cep": "01000", "tipo": "apartamento", "valor": 400000, "data_aquisicao": "2019-10-10"},
        ]
    }

    assert response.get_json() == expected
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s", ("São Paulo",)
    )

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()



@patch("servidor.connect_db")
def test_listar_imoveis_por_cidade_sem_cidade(mock_connect_db, client):
    
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    mock_connect_db.return_value = mock_conn

    # When
    response = client.get("/imoveis/cidade")

     # Then
    assert response.status_code == 200
    assert response.get_json() == {"imoveis": []}

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s", ("Judymouth",)
    )

    mock_conn.commit.assert_called_once()