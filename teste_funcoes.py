import pytest
from unittest.mock import patch, MagicMock
from servidor import app, connect_db

@pytest.fixture
def imoveis():
    """Cria imoveis de teste para a API."""
    app.config["TESTING"] = True
    with app.test_imoveis() as imoveis:
        yield imoveis

@patch("api.connect_db")  # Substituímos a função que conecta ao banco por um Mock
def test_get_imoveis(mock_connect_db, imoveis):
    """Testa a rota /alunos sem acessar o banco de dados real."""

    # Criamos um Mock para a conexão e o cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configuramos o Mock para retornar o cursor quando chamarmos conn.cursor()
    mock_conn.cursor.return_value = mock_cursor

    # Simulamos o retorno do banco de dados
    mock_cursor.fetchall.return_value = [
        ('Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
        ('Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30'),
        ('Taylor Ranch', 'Avenida', 'West Jennashire', 'Katherinefurt', '51116', 'apartamento', 815969.92, '2020-04-24')
    ]

    # Substituímos a função `connect_db` para retornar nosso Mock em vez de uma conexão real
    mock_connect_db.return_value = mock_conn

    # Fazemos a requisição para a API
    response = imoveis.get("/imoveis")

    # Verificamos se o código de status da resposta é 200 (OK)
    assert response.status_code == 200

    # Verificamos se os dados retornados estão corretos
    expected_response = {
        "imoveis": [
            {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep":"85184", "tipo":"casa em condominio", "valor":488423.52, "data_aquisicao":"2017-07-29"},
            {"id": 1, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep":"93354", "tipo":"casa em condominio", "valor":260069.89, "data_aquisicao":"2021-11-30"},
            {"id": 1, "logradouro": "Taylor Ranch", "tipo_logradouro": "Avenida", "bairro": "West Jennashire", "cidade": "Katherinefurt", "cep":"51116", "tipo":"apartamento", "valor":815969.92, "data_aquisicao":"2020-04-24"},
        ]
    }
    assert response.get_json() == expected_response

    # Verificamos se a consulta SQL foi executada corretamente
    mock_cursor.execute.assert_called_once_with("SELECT * from tbl_alunos")
    mock_cursor.execute.assert_called_once_with("SELECT * from")