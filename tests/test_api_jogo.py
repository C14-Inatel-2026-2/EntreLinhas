import pytest

import app as modulo_api
from db import conectar_bd, criar_tabelas


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    caminho = tmp_path / "partidas.sqlite3"

    def conectar_teste():
        return conectar_bd(str(caminho))

    conn = conectar_teste()
    criar_tabelas(conn)
    conn.close()
    monkeypatch.setattr(modulo_api, "conectar_bd", conectar_teste)
    modulo_api.app.config["TESTING"] = True
    with modulo_api.app.test_client() as cliente_flask:
        yield cliente_flask


def iniciar(cliente):
    resposta = cliente.post("/partida", json={"num_jogadores": 2})
    assert resposta.status_code == 201
    return resposta.get_json()


def test_inicio_entrega_estado_completo_para_interface(cliente):
    estado = iniciar(cliente)
    assert estado["id"] > 0
    assert estado["partida_id"] == estado["id"]
    assert estado["num_jogadores"] == 2
    assert estado["fase"] == "dica"
    assert estado["jogador_dica"] == 1
    assert estado["carta_secreta"] in {celula["coordenada"] for celula in estado["tabuleiro"]["celulas"]}
    assert estado["placar"] == {"acertos": 0, "erros": 0}
    assert len(estado["tabuleiro"]["celulas"]) == 9


def test_dica_palpite_e_placar_sao_persistidos(cliente):
    inicio = iniciar(cliente)
    rota = f"/partida/{inicio['id']}"

    resposta_dica = cliente.post(f"{rota}/dica", json={"dica": "cruzeiro"})
    assert resposta_dica.status_code == 200
    estado_dica = resposta_dica.get_json()
    assert estado_dica["fase"] == "palpite"
    assert estado_dica["dica"] == "cruzeiro"
    assert estado_dica["carta_secreta"] is None

    resposta_palpite = cliente.post(f"{rota}/palpite", json={"palpite": inicio["carta_secreta"]})
    assert resposta_palpite.status_code == 200
    estado = resposta_palpite.get_json()
    assert estado["fase"] == "dica"
    assert estado["jogador_dica"] == 2
    assert estado["placar"] == {"acertos": 1, "erros": 0}
    celula = next(c for c in estado["tabuleiro"]["celulas"] if c["coordenada"] == inicio["carta_secreta"])
    assert celula["estado"] == "acerto"
    assert cliente.get(f"{rota}/placar").get_json() == {"acertos": 1, "erros": 0}


def test_palpite_incorreto_descarta_carta_e_soma_erro(cliente):
    inicio = iniciar(cliente)
    rota = f"/partida/{inicio['id']}"
    outro_palpite = next(
        celula["coordenada"] for celula in inicio["tabuleiro"]["celulas"]
        if celula["coordenada"] != inicio["carta_secreta"]
    )

    assert cliente.post(f"{rota}/dica", json={"dica": "ponte"}).status_code == 200
    resposta = cliente.post(f"{rota}/palpite", json={"palpite": outro_palpite})
    assert resposta.status_code == 200
    estado = resposta.get_json()
    assert estado["placar"] == {"acertos": 0, "erros": 1}
    assert all(celula["estado"] == "vazia" for celula in estado["tabuleiro"]["celulas"])
    assert estado["carta_secreta"] != inicio["carta_secreta"]


def test_partida_termina_apos_todas_as_cartas(cliente):
    estado = iniciar(cliente)
    rota = f"/partida/{estado['id']}"

    for _ in range(9):
        carta = estado["carta_secreta"]
        resposta_dica = cliente.post(f"{rota}/dica", json={"dica": "teste"})
        assert resposta_dica.status_code == 200
        resposta_palpite = cliente.post(f"{rota}/palpite", json={"palpite": carta})
        assert resposta_palpite.status_code == 200
        estado = resposta_palpite.get_json()

    assert estado["fase"] == "final"
    assert estado["placar"] == {"acertos": 9, "erros": 0}
    assert "9 cartas posicionadas" in estado["resumo"]
    partida = cliente.get(rota).get_json()
    assert partida["pontuacao_final"] == 9
    assert partida["data_fim"] is not None


def test_api_rejeita_dica_invalida_e_palpite_fora_de_fase(cliente):
    estado = iniciar(cliente)
    rota = f"/partida/{estado['id']}"
    assert cliente.post(f"{rota}/palpite", json={"palpite": "A1"}).status_code == 409
    assert cliente.post(f"{rota}/dica", json={"dica": "duas palavras"}).status_code == 400
    assert cliente.post(f"{rota}/dica", json={"dica": "teste"}).status_code == 200
    assert cliente.post(f"{rota}/dica", json={"dica": "outra"}).status_code == 409
    assert cliente.post(f"{rota}/palpite", json={"palpite": "Z9"}).status_code == 400


@pytest.mark.parametrize("quantidade", [1, 7, True, "2"])
def test_inicio_rejeita_quantidade_invalida(cliente, quantidade):
    resposta = cliente.post("/partida", json={"num_jogadores": quantidade})
    assert resposta.status_code == 400
