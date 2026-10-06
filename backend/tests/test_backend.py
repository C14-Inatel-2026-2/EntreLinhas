import pytest
from unittest.mock import patch
from db import conectar_bd, criar_tabelas, criar_partida, consultar_partida
from app import app

# banco temporario na ram pra nao sujar o arquivo real
@pytest.fixture
def db_memoria():
    conn = conectar_bd(":memory:")
    criar_tabelas(conn)
    yield conn
    conn.close()

# cliente do flask pra simular as chamadas http
@pytest.fixture
def cliente_flask():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# teste sem mock: cria a partida no banco em memoria e busca em seguida
def test_criar_e_consultar_partida_sem_mock(db_memoria):
    partida_id = criar_partida(db_memoria, num_jogadores=4)
    assert partida_id > 0

    dados = consultar_partida(db_memoria, partida_id)
    assert dados is not None
    assert dados["id"] == partida_id
    assert dados["num_jogadores"] == 4

# teste sem mock: confere se os ids estao subindo sequencialmente
def test_id_partida_autoincremento(db_memoria):
    id1 = criar_partida(db_memoria, num_jogadores=2)
    id2 = criar_partida(db_memoria, num_jogadores=3)
    assert id2 == id1 + 1

# teste com mock: simula a resposta do banco sem precisar tocar nele
@patch("app.consultar_partida")
def test_obter_placar_com_mock(mock_consultar, cliente_flask):
    mock_consultar.return_value = {
        "id": 1,
        "data_inicio": "2026-09-23T10:00:00",
        "data_fim": None,
        "num_jogadores": 3,
        "pontuacao_final": 10
    }

    res = cliente_flask.get("/partida/1")
    assert res.status_code == 200
    dados = res.get_json()
    assert dados["id"] == 1
    assert dados["pontuacao_final"] == 10

# teste negativo: tenta dar palpite em uma partida que nao existe
def test_palpite_partida_inexistente_retorna_404(cliente_flask):
    payload = {
        "jogador": "Henrique",
        "dica": "Sol",
        "coordenada_correta": "A1",
        "coordenada_tentada": "A2"
    }
    
    res = cliente_flask.post("/partida/99999/palpite", json=payload)
    assert res.status_code == 404
    dados = res.get_json()
    assert dados["erro"] == "Partida não encontrada"