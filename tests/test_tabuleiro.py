# tests/test_tabuleiro.py

from unittest.mock import MagicMock
from src.tabuleiro import Tabuleiro

# --- 1. TESTE SEM MOCK: Validar coordenada existente (True) ---
def test_coordenada_valida_sucesso():
    tab = Tabuleiro(
        topicos_linhas=["A", "B", "C", "D", "E"],
        topicos_colunas=["1", "2", "3", "4", "5"]
    )
    assert tab.coordenada_valida("A1") is True
    assert tab.coordenada_valida("c3") is True  # Testa conversão para maiúscula


# --- 2. TESTE SEM MOCK: Validar dimensão da grade (5x5 para cartas e 5 linhas/colunas) ---
def test_dimensao_grade():
    linhas = ["A", "B", "C", "D", "E"]
    colunas = ["1", "2", "3", "4", "5"]
    tab = Tabuleiro(linhas, colunas)
    
    assert len(tab.linhas) == 5
    assert len(tab.colunas) == 5
    assert len(tab.grade) == 5
    assert all(len(linha) == 5 for linha in tab.grade)


# --- 3. TESTE COM MOCK: Simular tópicos e testar registro de acerto numa célula mockada ---
def test_registrar_jogada_com_mock():
    tab = Tabuleiro(["A", "B", "C", "D", "E"], ["1", "2", "3", "4", "5"])
    
    # Criando um mock para representar uma carta/objeto que será inserido
    carta_mock = MagicMock()
    carta_mock.__str__.return_value = "CartaTeste"
    
    # Registra a jogada na coordenada A1
    sucesso = tab.registrar_jogada("A1", carta_mock)
    
    assert sucesso is True
    # Verifica se a célula foi preenchida corretamente com o objeto mockado
    assert tab.grade[0][0] == carta_mock


# --- 4. TESTE NEGATIVO: Coordenada fora da grade ("Z9") deve retornar False / Erro ---
def test_coordenada_invalida_negativo():
    tab = Tabuleiro(
        topicos_linhas=["A", "B", "C", "D", "E"],
        topicos_colunas=["1", "2", "3", "4", "5"]
    )
    
    # Coordenadas inexistentes ou formatos errados devem retornar False
    assert tab.coordenada_valida("Z9") is False
    assert tab.coordenada_valida("A9") is False
    assert tab.coordenada_valida("F1") is False
    assert tab.coordenada_valida(123) is False  # Tipo inválido