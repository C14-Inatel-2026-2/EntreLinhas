import sqlite3
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

def conectar_bd(db_path="jogo.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas(conn):
    with conn:
        conn.execute(SCHEMA_PARTIDAS)
        conn.execute(SCHEMA_JOGADAS)

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