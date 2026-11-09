"""Testes de caracterização do placar e do tabuleiro (issue #66).

Fixam o comportamento atual antes dos refactorings: se a extração das funções
mudar algum número ou o formato do JSON, estes testes falham.
"""
from unittest.mock import patch

import pytest

import app as modulo_api
from db import conectar_bd, consultar_jogadas, criar_tabelas
from jogo import montar_estado

# Ordem fixa das cartas, injetada por mock no lugar do embaralhamento.
ORDEM_CARTAS = ["B2", "A1", "C3", "A3", "C1", "B1", "A2", "C2", "B3"]
PALAVRAS = ["mar", "casa", "música", "noite", "festa", "viagem"]

# Roteiro da partida: (carta secreta, palpite). None = tempo esgotado.
RODADAS = [
    ("B2", "B2"),  # acerto
    ("A1", "C3"),  # erro
    ("C3", "C3"),  # acerto
    ("A3", None),  # erro por tempo esgotado
    ("C1", "C1"),  # acerto
    ("B1", "A2"),  # erro
    ("A2", "A2"),  # acerto
    ("C2", "B3"),  # erro
    ("B3", "B3"),  # acerto
]

TABULEIRO_LINHAS = [
    {"id": "A", "palavra": "mar"},
    {"id": "B", "palavra": "casa"},
    {"id": "C", "palavra": "música"},
]
TABULEIRO_COLUNAS = [
    {"id": "1", "palavra": "noite"},
    {"id": "2", "palavra": "festa"},
    {"id": "3", "palavra": "viagem"},
]
CELULAS_FINAIS = [
    {"coordenada": "A1", "estado": "vazia"},
    {"coordenada": "A2", "estado": "acerto"},
    {"coordenada": "A3", "estado": "vazia"},
    {"coordenada": "B1", "estado": "vazia"},
    {"coordenada": "B2", "estado": "acerto"},
    {"coordenada": "B3", "estado": "acerto"},
    {"coordenada": "C1", "estado": "acerto"},
    {"coordenada": "C2", "estado": "vazia"},
    {"coordenada": "C3", "estado": "acerto"},
]


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


def iniciar_com_ordem_fixa(cliente):
    """Cria a partida com as cartas na ORDEM_CARTAS, usando mock no embaralhamento."""
    with patch("app.criar_cartas", return_value=list(ORDEM_CARTAS)) as embaralhar:
        estado = cliente.post("/partida", json={"num_jogadores": 2}).get_json()
    embaralhar.assert_called_once_with()
    assert estado["carta_secreta"] == ORDEM_CARTAS[0]
    return estado


def jogar_rodada(cliente, rota, turno, palpite):
    """Envia a dica e o palpite; palpite None deixa o tempo de dois minutos esgotar."""
    if palpite is not None:
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
        return cliente.post(f"{rota}/palpite", json={"palpite": palpite}).get_json()
    with patch("jogo.time.time", return_value=1000):
        cliente.post(f"{rota}/dica", json={"dica": "ponte"})
    with patch("jogo.time.time", return_value=1120):
        return cliente.post(f"{rota}/tempo", json={"turno": turno, "fase": "palpite"}).get_json()


def jogadas_salvas(partida_id):
    conn = modulo_api.conectar_bd()
    try:
        return consultar_jogadas(conn, partida_id)
    finally:
        conn.close()


# --- Refactoring 1: cálculo do placar ---

def test_placar_e_igual_no_estado_na_rota_placar_e_na_pontuacao_final(cliente):
    """Teste com mock: as quatro rotas que calculam acertos devem concordar."""
    estado = iniciar_com_ordem_fixa(cliente)
    rota = f"/partida/{estado['id']}"

    for turno, (carta, palpite) in enumerate(RODADAS):
        assert estado["carta_secreta"] == carta
        estado = jogar_rodada(cliente, rota, turno, palpite)
        assert estado["placar"] == cliente.get(f"{rota}/placar").get_json()

    assert estado["fase"] == "final"
    assert estado["placar"] == {"acertos": 5, "erros": 4}
    assert cliente.get(rota).get_json()["pontuacao_final"] == 5
    assert estado["desempenho"]["classificacao"] == "Mediano"
    assert estado["resumo"] == "Partida encerrada: 5 cartas posicionadas e 4 descartadas."
    assert estado["tabuleiro"]["celulas"] == CELULAS_FINAIS


def test_encerramento_antecipado_grava_a_mesma_pontuacao_do_placar(cliente):
    estado = iniciar_com_ordem_fixa(cliente)
    rota = f"/partida/{estado['id']}"
    for turno, (_, palpite) in enumerate(RODADAS[:3]):
        jogar_rodada(cliente, rota, turno, palpite)

    final = cliente.post(f"{rota}/encerrar").get_json()

    assert final["placar"] == {"acertos": 2, "erros": 1}
    assert cliente.get(f"{rota}/placar").get_json() == final["placar"]
    assert cliente.get(rota).get_json()["pontuacao_final"] == 2
    assert final["desempenho"]["concluida"] is False
    assert final["desempenho"]["cartas_restantes"] == 6


def test_palpite_em_coordenada_ja_preenchida_e_recusado(cliente):
    estado = iniciar_com_ordem_fixa(cliente)
    rota = f"/partida/{estado['id']}"
    jogar_rodada(cliente, rota, 0, "B2")
    cliente.post(f"{rota}/dica", json={"dica": "ponte"})

    resposta = cliente.post(f"{rota}/palpite", json={"palpite": "B2"})

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": "Essa coordenada já foi preenchida"}
    assert len(jogadas_salvas(estado["id"])) == 1
    atual = cliente.post(f"{rota}/tempo").get_json()
    assert (atual["fase"], atual["turno"]) == ("palpite", 1)
    assert atual["placar"] == {"acertos": 1, "erros": 0}


def test_dica_e_gravada_junto_com_a_jogada(cliente):
    """RF-DIC-04: a jogada guarda jogador, dica e as duas coordenadas."""
    estado = iniciar_com_ordem_fixa(cliente)
    rota = f"/partida/{estado['id']}"
    cliente.post(f"{rota}/dica", json={"dica": "  cruzeiro  "})
    cliente.post(f"{rota}/palpite", json={"palpite": "C3"})

    [jogada] = jogadas_salvas(estado["id"])

    assert jogada["jogador"] == str(estado["jogador_dica"])
    assert jogada["dica"] == "cruzeiro"
    assert jogada["coordenada_correta"] == "B2"
    assert jogada["coordenada_tentada"] == "C3"
    assert jogada["acertou"] == 0
    assert jogada["ordem"] == 1


# --- Refactoring 2: montagem do tabuleiro (JSON completo de montar_estado) ---

def jogadas_do_roteiro(quantidade):
    return [
        {"coordenada_correta": carta, "coordenada_tentada": palpite, "acertou": int(carta == palpite)}
        for carta, palpite in RODADAS[:quantidade]
    ]


def progresso_fixo(indice, fase):
    return {
        "cartas": list(ORDEM_CARTAS),
        "indice": indice,
        "fase": fase,
        "dica": None,
        "palavras": list(PALAVRAS),
        "ordem_jogadores": [2, 1] * 4 + [2],
        "turno_inicio": None,
    }


def test_montar_estado_no_meio_da_partida_preserva_o_json():
    partida = {"id": 7, "num_jogadores": 2, "data_inicio": None, "data_fim": None}

    estado = montar_estado(partida, progresso_fixo(2, "dica"), jogadas_do_roteiro(2))

    assert estado == {
        "id": 7,
        "partida_id": 7,
        "num_jogadores": 2,
        "fase": "dica",
        "jogador_dica": 2,
        "carta_secreta": "C3",
        "dica": None,
        "tabuleiro": {
            "linhas": TABULEIRO_LINHAS,
            "colunas": TABULEIRO_COLUNAS,
            "celulas": [
                {"coordenada": coordenada, "estado": "acerto" if coordenada == "B2" else "vazia"}
                for coordenada in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
            ],
        },
        "placar": {"acertos": 1, "erros": 1},
        "turno": 2,
        "duracao_segundos": None,
        "tempo_restante": None,
    }


def test_montar_estado_no_fim_da_partida_preserva_o_json():
    partida = {
        "id": 7,
        "num_jogadores": 2,
        "data_inicio": "2026-11-05T10:00:00",
        "data_fim": "2026-11-05T10:05:00",
    }

    estado = montar_estado(partida, progresso_fixo(9, "final"), jogadas_do_roteiro(9), "Palpite correto!")

    assert estado == {
        "id": 7,
        "partida_id": 7,
        "num_jogadores": 2,
        "fase": "final",
        "jogador_dica": 2,
        "carta_secreta": None,
        "dica": None,
        "tabuleiro": {
            "linhas": TABULEIRO_LINHAS,
            "colunas": TABULEIRO_COLUNAS,
            "celulas": CELULAS_FINAIS,
        },
        "placar": {"acertos": 5, "erros": 4},
        "turno": 9,
        "duracao_segundos": 300,
        "tempo_restante": None,
        "mensagem": "Palpite correto!",
        "desempenho": {
            "classificacao": "Mediano",
            "concluida": True,
            "cartas_restantes": 0,
            "total_cartas": 9,
        },
        "resumo": "Partida encerrada: 5 cartas posicionadas e 4 descartadas.",
    }
