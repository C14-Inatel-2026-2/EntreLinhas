"""Testes do cronômetro por turno e do tempo total da partida."""
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


def partida_em(cliente, fase, segundos):
    """Cria a partida na fase pedida e recua o início do turno em `segundos` (sem sleep)."""
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    if fase == "palpite":
        cliente.post(f"/partida/{estado['id']}/dica", json={"dica": "ponte"})
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


@pytest.mark.parametrize("rota, fase", [("dica", "dica"), ("tempo", "dica"),
                                         ("palpite", "palpite"), ("tempo", "palpite")])
def test_as_tres_rotas_usam_a_mesma_regra_de_expiracao(cliente, rota, fase):
    limite = TEMPO_DICA if fase == "dica" else TEMPO_PALPITE
    for segundos, deve_penalizar in [(limite + TOLERANCIA - 1, False), (limite + TOLERANCIA + 1, True)]:
        estado = partida_em(cliente, fase, segundos)
        corpo = {"dica": {"dica": "ponte"}, "palpite": {"palpite": estado["carta_secreta"]}, "tempo": {}}[rota]
        novo = cliente.post(f"/partida/{estado['id']}/{rota}", json=corpo).get_json()
        assert novo["placar"]["erros"] == (1 if deve_penalizar else 0), (rota, fase, segundos)
        assert novo.get("mensagem", "").startswith("Tempo esgotado") is deve_penalizar


def test_tempo_ignora_turno_antigo_e_estado_expoe_turno_e_expira_em(cliente):
    estado = partida_em(cliente, "dica", TEMPO_DICA + TOLERANCIA + 5)
    rota = f"/partida/{estado['id']}/tempo"
    antigo = cliente.post(rota, json={"turno": estado["turno"], "fase": "palpite"}).get_json()
    assert antigo["placar"]["erros"] == 0 and antigo["expira_em"] == 0  # não puniu o turno errado
    atual = cliente.post(rota, json={"turno": estado["turno"], "fase": "dica"}).get_json()
    assert atual["placar"]["erros"] == 1 and atual["turno"] == estado["turno"] + 1
    assert TEMPO_DICA + TOLERANCIA - 2 <= estado["expira_em"] <= TEMPO_DICA + TOLERANCIA