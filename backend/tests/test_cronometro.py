"""Tempo total livre e avaliação do modo Expresso (3 × 3)."""
from datetime import datetime
from unittest.mock import patch

import pytest

import app as modulo_api
from db import conectar_bd, criar_tabelas
from jogo import avaliar_desempenho, duracao_segundos


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


def test_duracao_total_e_fixa_apos_finalizar():
    partida = {"data_inicio": "2026-11-05T10:00:00", "data_fim": None}
    with patch("jogo.datetime", wraps=datetime) as falso:
        falso.now.return_value = datetime(2026, 11, 5, 10, 3, 25)
        assert duracao_segundos(partida) == 205
        falso.now.assert_called_once_with()
        partida["data_fim"] = "2026-11-05T10:03:25"
        falso.now.reset_mock()
        falso.now.return_value = datetime(2026, 11, 6)
        assert duracao_segundos(partida) == 205
        falso.now.assert_not_called()


@pytest.mark.parametrize("acertos,classe", [
    (0, "Fracasso"), (3, "Fracasso"), (4, "Mediano"), (5, "Mediano"),
    (6, "Bom"), (7, "Bom"), (8, "Espetacular"), (9, "Espetacular"),
])
def test_classificacao_oficial_depende_apenas_dos_acertos(acertos, classe):
    resultado = avaliar_desempenho(acertos, 9, 9)
    assert resultado["classificacao"] == classe
    assert "dentro_referencia" not in resultado
    assert "referencia_segundos" not in resultado
    assert resultado["concluida"] is True
    assert resultado["cartas_restantes"] == 0


def test_encerramento_antecipado_tem_avaliacao_parcial():
    resultado = avaliar_desempenho(4, 5, 9)
    assert resultado["classificacao"] == "Mediano"
    assert resultado["concluida"] is False
    assert resultado["cartas_restantes"] == 4


def test_tempo_nao_descarta_cartas_nem_bloqueia_dica_ou_palpite(cliente):
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    rota = f"/partida/{estado['id']}"
    # Simula muito tempo transcorrido, sem esperar nem alterar o relógio real.
    with patch("jogo.datetime", wraps=datetime) as falso:
        falso.now.return_value = datetime(2099, 1, 1)
        for _ in range(2):
            consulta = cliente.post(f"{rota}/tempo").get_json()
            assert consulta["fase"] == "dica"
            assert consulta["turno"] == 0
            assert consulta["placar"] == {"acertos": 0, "erros": 0}
        dica = cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        assert dica.status_code == 200
        assert dica.get_json()["fase"] == "palpite"
        assert cliente.post(f"{rota}/tempo").get_json()["fase"] == "palpite"
        resposta = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]})
        assert resposta.status_code == 200
        assert resposta.get_json()["placar"] == {"acertos": 1, "erros": 0}
        falso.now.assert_called()
    assert "desempenho" not in dica.get_json()
    assert dica.get_json()["tempo_restante"] == 120
    assert "expira_em" not in dica.get_json()


@pytest.mark.parametrize("natural", [True, False])
def test_resultado_usa_data_final_persistida_e_nao_relogio_em_andamento(cliente, natural):
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    rota = f"/partida/{estado['id']}"
    with patch("jogo.datetime", wraps=datetime) as falso:
        # Um estado desatualizado de partida usaria este valor incorreto ao finalizar.
        falso.now.return_value = datetime(2099, 1, 1)
        if natural:
            for _ in range(9):
                cliente.post(f"{rota}/dica", json={"dica": "ponte"})
                estado = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]}).get_json()
        else:
            estado = cliente.post(f"{rota}/encerrar").get_json()
        persistida = cliente.get(rota).get_json()
        esperado = int((datetime.fromisoformat(persistida["data_fim"]) - datetime.fromisoformat(persistida["data_inicio"])).total_seconds())
        assert estado["duracao_segundos"] == esperado
        assert estado["desempenho"]["concluida"] is natural
        assert estado["desempenho"]["classificacao"] == ("Espetacular" if natural else "Fracasso")
        repetida = cliente.post(f"{rota}/encerrar").get_json()
        consulta = cliente.post(f"{rota}/tempo").get_json()
        assert repetida["duracao_segundos"] == consulta["duracao_segundos"] == esperado
        assert repetida["desempenho"] == estado["desempenho"] == consulta["desempenho"]


@pytest.mark.parametrize("segundos,expirou", [(119.999, False), (120, True), (121, True)])
@pytest.mark.parametrize("endpoint", ["tempo", "palpite"])
def test_palpite_tem_dois_minutos_apenas_apos_dica(cliente, segundos, expirou, endpoint):
    with patch("jogo.time.time", return_value=1000):
        estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    rota = f"/partida/{estado['id']}"
    with patch("jogo.time.time", return_value=5000):
        assert cliente.post(f"{rota}/tempo").get_json()["placar"]["erros"] == 0
        dica = cliente.post(f"{rota}/dica", json={"dica": "ponte"}).get_json()
        assert dica["tempo_restante"] == 120
    with patch("jogo.time.time", return_value=5000 + segundos) as relogio:
        payload = {"palpite": estado["carta_secreta"], "turno": 0, "fase": "palpite"}
        resposta = cliente.post(f"{rota}/{endpoint}", json=payload).get_json()
        if expirou:
            assert resposta["placar"]["erros"] == 1
            assert resposta["fase"] in ("dica", "palpite", "final")
        else:
            assert resposta["placar"]["erros"] == 0
        relogio.assert_called()


def test_expiracao_da_ultima_carta_finaliza_e_preserva_duracao(cliente):
    estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    rota = f"/partida/{estado['id']}"
    for _ in range(8):
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        estado = cliente.post(f"{rota}/palpite", json={"palpite": estado["carta_secreta"]}).get_json()
    with patch("jogo.time.time", return_value=1000):
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
    with patch("jogo.time.time", return_value=1120) as relogio:
        final = cliente.post(f"{rota}/tempo", json={"turno": 8, "fase": "palpite"}).get_json()
        relogio.assert_called()
    assert final["fase"] == "final"
    assert final["placar"] == {"acertos": 8, "erros": 1}
    assert final["desempenho"]["classificacao"] == "Espetacular"
    assert final["tempo_restante"] is None
    assert cliente.post(f"{rota}/tempo").get_json()["duracao_segundos"] == final["duracao_segundos"]
