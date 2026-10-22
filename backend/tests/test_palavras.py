"""Catálogo, sorteio persistido e migração de bancos anteriores."""
import json

from db import conectar_bd, criar_tabelas, criar_partida, criar_estado, consultar_estado
from jogo import criar_cartas


def test_catalogo_tem_200_palavras_e_inicializacao_idempotente():
    with conectar_bd(":memory:") as conn:
        criar_tabelas(conn)
        criar_tabelas(conn)
        palavras = [row["palavra"] for row in conn.execute("SELECT palavra FROM palavras")]
        assert len(palavras) == len(set(palavras)) == 200
        assert all(palavra.strip() == palavra and len(palavra.split()) == 1 for palavra in palavras)


def test_sorteio_consulta_banco_sem_repeticao_e_persiste_apos_reconectar(tmp_path):
    caminho = str(tmp_path / "jogo.db")
    conn = conectar_bd(caminho)
    criar_tabelas(conn)
    # Um catálogo diferente comprova que a seleção vem do banco, e não da lista Python.
    with conn:
        conn.execute("DELETE FROM palavras")
        conn.executemany("INSERT INTO palavras (palavra) VALUES (?)", [(f"opcao{i}",) for i in range(30)])
    selecoes = []
    for _ in range(10):
        partida = criar_partida(conn, 2)
        criar_estado(conn, partida, criar_cartas())
        palavras = consultar_estado(conn, partida)["palavras"]
        assert len(palavras) == len(set(palavras)) == 6
        assert all(palavra.startswith("opcao") for palavra in palavras)
        selecoes.append(tuple(palavras))
    conn.close()
    with conectar_bd(caminho) as conn:
        assert tuple(consultar_estado(conn, partida)["palavras"]) == selecoes[-1]
    assert len(set(selecoes)) > 1


def test_migracao_preserva_palavras_e_progresso_de_partida_antiga():
    with conectar_bd(":memory:") as conn:
        conn.execute("CREATE TABLE estados_partida (partida_id INTEGER PRIMARY KEY, cartas TEXT, indice INTEGER, fase TEXT, dica TEXT)")
        conn.execute("INSERT INTO estados_partida VALUES (1, ?, 2, 'palpite', 'barco')", (json.dumps(["A1", "A2", "A3"]),))
        criar_tabelas(conn)
        criar_tabelas(conn)
        estado = consultar_estado(conn, 1)
        assert estado["palavras"] == ["mar", "casa", "música", "noite", "festa", "viagem"]
        assert estado["indice"] == 2
        assert estado["dica"] == "barco"
