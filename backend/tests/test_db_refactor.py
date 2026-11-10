import pytest
import sqlite3
from db import conectar_bd, criar_tabelas

def test_conectar_bd_retorna_conexao_valida():
    conn = conectar_bd()
    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_criar_tabelas_idempotencia():
    conn = conectar_bd()
    try:
        criar_tabelas(conn)
        criar_tabelas(conn)
    finally:
        conn.close()