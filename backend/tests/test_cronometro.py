from datetime import datetime
from unittest.mock import patch

import pytest

import app as modulo_api
from db import conectar_bd, criar_tabelas
from jogo import TEMPO_DICA, TEMPO_PALPITE, TOLERANCIA, duracao_segundos, tempo_esgotado


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    caminho = tmp_path / "partidas.sqlite3"
    conn = conectar_bd(str(caminho))
    criar_tabelas(conn)
    conn.close()
    monkeypatch.setattr(modulo_api, "conectar_bd", lambda: conectar_bd(str(caminho)))
    modulo_api.app.config["TESTING"] = True
    with modulo_api.app.test_client() as cliente_flask:
        yield cliente_flask


def iniciar_e_envelhecer(cliente, segundos):
    """Cria a partida e recua o início do turno (simula `segundos` passados, sem sleep)."""
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    conn = modulo_api.conectar_bd()
    with conn:
        conn.execute("UPDATE estados_partida SET turno_inicio = turno_inicio - ? WHERE partida_id = ?",
                     (segundos, estado["id"]))
    conn.close()
    return estado


def test_tempo_esgotado_respeita_limite_e_tolerancia():
    """Com MOCK do relógio: dentro da tolerância ainda vale; depois dela, esgotou."""
    progresso = {"fase": "dica", "turno_inicio": 1000.0}
    with patch("jogo.time") as relogio:
        relogio.time.return_value = 1000.0 + TEMPO_DICA + TOLERANCIA
        assert tempo_esgotado(progresso) is False
        relogio.time.return_value = 1000.0 + TEMPO_DICA + TOLERANCIA + 0.1
        assert tempo_esgotado(progresso) is True
        assert tempo_esgotado({"fase": "final", "turno_inicio": 1000.0}) is False


def test_duracao_da_partida_usa_agora_simulado():
    """Com MOCK de datetime.now(): 10:00:00 -> 10:03:25 são 205 segundos."""
    partida = {"data_inicio": "2026-11-05T10:00:00", "data_fim": None}
    with patch("jogo.datetime", wraps=datetime) as falso:
        falso.now.return_value = datetime(2026, 11, 5, 10, 3, 25)
        assert duracao_segundos(partida) == 205


def test_palpite_fora_do_tempo_conta_como_erro(cliente):
    estado = iniciar_e_envelhecer(cliente, 0)
    rota = f"/partida/{estado['id']}"
    cliente.post(f"{rota}/dica", json={"dica": "ponte"})
    conn = modulo_api.conectar_bd()
    with conn:
        conn.execute("UPDATE estados_partida SET turno_inicio = turno_inicio - ?",
                     (TEMPO_PALPITE + TOLERANCIA + 5,))
    conn.close()

    resposta = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]})  # certo, mas atrasado
    assert resposta.status_code == 200
    novo = resposta.get_json()
    assert novo["mensagem"].startswith("Tempo esgotado")
    assert novo["placar"] == {"acertos": 0, "erros": 1}


def test_rota_tempo_so_penaliza_depois_do_limite(cliente):
    estado = iniciar_e_envelhecer(cliente, 10)
    antes = cliente.post(f"/partida/{estado['id']}/tempo").get_json()
    assert "mensagem" not in antes and antes["placar"]["erros"] == 0

    estado = iniciar_e_envelhecer(cliente, TEMPO_DICA + 1)
    depois = cliente.post(f"/partida/{estado['id']}/tempo").get_json()
    assert depois["mensagem"].startswith("Tempo esgotado")
    assert depois["placar"] == {"acertos": 0, "erros": 1}