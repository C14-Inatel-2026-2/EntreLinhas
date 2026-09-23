import sqlite3
import json
from datetime import datetime

SCHEMA_PARTIDAS = """
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_inicio TEXT NOT NULL,
    data_fim TEXT,
    num_jogadores INTEGER NOT NULL,
    pontuacao_final INTEGER DEFAULT 0
);
"""

SCHEMA_JOGADAS = """
CREATE TABLE IF NOT EXISTS jogadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER NOT NULL,
    jogador TEXT NOT NULL,
    dica TEXT NOT NULL,
    coordenada_correta TEXT NOT NULL,
    coordenada_tentada TEXT,
    acertou INTEGER NOT NULL,
    ordem INTEGER NOT NULL,
    FOREIGN KEY (partida_id) REFERENCES partidas(id)
);
"""

SCHEMA_ESTADOS = """
CREATE TABLE IF NOT EXISTS estados_partida (
    partida_id INTEGER PRIMARY KEY,
    cartas TEXT NOT NULL,
    indice INTEGER NOT NULL DEFAULT 0,
    fase TEXT NOT NULL DEFAULT 'dica',
    dica TEXT,
    FOREIGN KEY (partida_id) REFERENCES partidas(id)
);
"""

def conectar_bd(db_path="jogo.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas(conn):
    with conn:
        conn.execute(SCHEMA_PARTIDAS)
        conn.execute(SCHEMA_JOGADAS)
        conn.execute(SCHEMA_ESTADOS)

def criar_partida(conn, num_jogadores):
    data_inicio = datetime.now().isoformat()
    query = "INSERT INTO partidas (data_inicio, num_jogadores) VALUES (?, ?)"
    with conn:
        cursor = conn.execute(query, (data_inicio, num_jogadores))
        return cursor.lastrowid

def consultar_partida(conn, partida_id):
    query = "SELECT * FROM partidas WHERE id = ?"
    cursor = conn.execute(query, (partida_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None

def salvar_jogada(conn, partida_id, jogador, dica, coord_correta, coord_tentada, ordem):
    acertou = 1 if coord_correta == coord_tentada else 0
    query = """
    INSERT INTO jogadas (partida_id, jogador, dica, coordenada_correta, coordenada_tentada, acertou, ordem)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with conn:
        cursor = conn.execute(
            query, 
            (partida_id, jogador, dica, coord_correta, coord_tentada, acertou, ordem)
        )
        return cursor.lastrowid


def criar_estado(conn, partida_id, cartas):
    with conn:
        conn.execute(
            "INSERT INTO estados_partida (partida_id, cartas) VALUES (?, ?)",
            (partida_id, json.dumps(cartas)),
        )


def consultar_estado(conn, partida_id):
    row = conn.execute(
        "SELECT * FROM estados_partida WHERE partida_id = ?", (partida_id,)
    ).fetchone()
    if row is None:
        return None
    estado = dict(row)
    estado["cartas"] = json.loads(estado["cartas"])
    return estado


def atualizar_estado(conn, partida_id, indice, fase, dica=None):
    with conn:
        conn.execute(
            "UPDATE estados_partida SET indice = ?, fase = ?, dica = ? WHERE partida_id = ?",
            (indice, fase, dica, partida_id),
        )


def consultar_jogadas(conn, partida_id):
    return [dict(row) for row in conn.execute(
        "SELECT * FROM jogadas WHERE partida_id = ? ORDER BY ordem", (partida_id,)
    )]


def finalizar_partida(conn, partida_id, pontuacao):
    with conn:
        conn.execute(
            "UPDATE partidas SET data_fim = ?, pontuacao_final = ? WHERE id = ?",
            (datetime.now().isoformat(), pontuacao, partida_id),
        )
