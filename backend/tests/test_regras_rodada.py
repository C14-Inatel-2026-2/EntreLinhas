"""Testes de caracterização das regras de dica e de avanço da rodada (issue #8).

Fixam, pela API real, o que a rota de dica aceita ou recusa e o momento em que
a partida chega à fase final, antes de essas regras irem para `backend/jogo.py`.
"""
from unittest.mock import patch

import pytest

import app as modulo_api
from db import conectar_bd, criar_tabelas

MENSAGEM_DICA = "A dica deve ter uma única palavra de até 60 caracteres"


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    caminho = tmp_path / "partidas.sqlite3"
    # As rotas abrem a conexão por get_db_connection, que lê DATABASE_PATH.
    monkeypatch.setenv("DATABASE_PATH", str(caminho))
    conn = conectar_bd(str(caminho))
    criar_tabelas(conn)
    conn.close()
    monkeypatch.setattr(modulo_api, "conectar_bd", lambda: conectar_bd(str(caminho)))
    modulo_api.app.config["TESTING"] = True
    with modulo_api.app.test_client() as cliente_flask:
        yield cliente_flask


def iniciar(cliente):
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    return estado, f"/partida/{estado['id']}"


# --- Regra da dica: uma única palavra, com até 60 caracteres ---

@pytest.mark.parametrize("corpo", [
    {"dica": ""},
    {"dica": "   "},
    {"dica": "duas palavras"},
    {"dica": "a" * 61},
    {"dica": None},
    {"dica": 123},
    {"dica": ["ponte"]},
    {},
    ["ponte"],
    "ponte",
])
def test_dica_invalida_e_recusada_sem_mudar_a_fase(cliente, corpo):
    _, rota = iniciar(cliente)

    resposta = cliente.post(f"{rota}/dica", json=corpo)

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": MENSAGEM_DICA}
    atual = cliente.post(f"{rota}/tempo").get_json()
    assert (atual["fase"], atual["turno"], atual["dica"]) == ("dica", 0, None)


def test_dica_sem_corpo_json_e_recusada(cliente):
    _, rota = iniciar(cliente)

    resposta = cliente.post(f"{rota}/dica", data="ponte", content_type="text/plain")

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": MENSAGEM_DICA}


@pytest.mark.parametrize("enviada,exibida", [
    ("ponte", "ponte"),
    ("  ponte  ", "ponte"),
    ("guarda-chuva", "guarda-chuva"),
    ("a" * 60, "a" * 60),
    ("  " + "a" * 60 + "  ", "a" * 60),
])
def test_dica_valida_inicia_o_palpite_sem_os_espacos_das_pontas(cliente, enviada, exibida):
    _, rota = iniciar(cliente)

    resposta = cliente.post(f"{rota}/dica", json={"dica": enviada})

    assert resposta.status_code == 200
    estado = resposta.get_json()
    assert (estado["fase"], estado["turno"], estado["dica"]) == ("palpite", 0, exibida)
    assert estado["carta_secreta"] is None


# --- Avanço da rodada: volta para a dica até a nona carta, depois fase final ---

@pytest.mark.parametrize("ultima_carta", ["palpite", "tempo esgotado"])
def test_fase_final_chega_exatamente_na_nona_carta(cliente, ultima_carta):
    estado, rota = iniciar(cliente)
    for turno in range(8):
        assert (estado["fase"], estado["turno"]) == ("dica", turno)
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        estado = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]}).get_json()
    assert (estado["fase"], estado["turno"]) == ("dica", 8)
    assert "desempenho" not in estado
    assert cliente.get(rota).get_json()["data_fim"] is None

    if ultima_carta == "palpite":
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        estado = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]}).get_json()
        placar = {"acertos": 9, "erros": 0}
    else:
        # Mock do relógio: a dica entra no instante 1000 e o prazo de 120 s vence.
        with patch("jogo.time.time", return_value=1000):
            cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        with patch("jogo.time.time", return_value=1120):
            estado = cliente.post(f"{rota}/tempo", json={"turno": 8, "fase": "palpite"}).get_json()
        placar = {"acertos": 8, "erros": 1}

    assert (estado["fase"], estado["turno"]) == ("final", 9)
    assert estado["carta_secreta"] is None
    assert estado["placar"] == placar
    assert estado["desempenho"]["concluida"] is True
    registro = cliente.get(rota).get_json()
    assert registro["data_fim"] is not None
    assert registro["pontuacao_final"] == placar["acertos"]
    assert cliente.post(f"{rota}/dica", json={"dica": "nova"}).status_code == 409
    assert cliente.post(f"{rota}/palpite", json={"palpite": "A1"}).status_code == 409
