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
    # cria mocks para simular a conexão e o cursor do banco
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # quando conn.cursor() for chamado, retorna o cursor falso
    mock_conn.cursor.return_value = mock_cursor
    # simula o retorno do banco (uma linha da tabela imoveis)
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

    # a função connect_db() retorna a conexão falsa
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

    # verifica se o SQL correto foi executado
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
    # simula banco retornando nenhum resultado
    mock_cursor.fetchone.return_value = None
    mock_connect_db.return_value = mock_conn
    # When
    response = client.get("/imoveis/9999")
    # Then

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    # verifica SQL executado
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (9999,)
    )