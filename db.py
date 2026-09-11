import sqlite3

# Scripts DDL para criação das tabelas
SCHEMA_PARTIDAS = """
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_inicio TEXT NOT NULL,
    data_fim TEXT,
    num_jogadores INTEGER NOT NULL,
    pontuacao_final INTEGER
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

def conectar_bd(db_path: str = "jogo.db") -> sqlite3.Connection:
    """Abre conexão com o SQLite e ativa o suporte a Chaves Estrangeiras."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas(conn: sqlite3.Connection) -> None:
    """Executa a criação das tabelas no banco de dados."""
    with conn:
        conn.execute(SCHEMA_PARTIDAS)
        conn.execute(SCHEMA_JOGADAS)
