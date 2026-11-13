"""Modelo de domínio em memória: jogadores, baralho e tabuleiro.

A API web não usa esta classe. Na API, o estado da partida fica no SQLite e as
regras são funções de `backend/jogo.py`; apenas `Baralho` é compartilhado.
A decisão está registrada na issue #8 e em "Arquitetura e API" no README.
"""

from .Baralho import Baralho
from .tabuleiro import Tabuleiro


class Jogo:
    """Reúne o baralho, o tabuleiro e os jogadores de uma partida em memória.

    O baralho e o tabuleiro devem ser criados com as mesmas coordenadas;
    a dimensão da grade é definida por eles, não por esta classe. As cartas
    e células permanecem sob responsabilidade dessas instâncias, sem cópias
    ou alterações durante a inicialização.
    """

    def __init__(self, baralho: Baralho, tabuleiro: Tabuleiro, jogadores: list) -> None:
        if not isinstance(jogadores, list):
            raise TypeError("Os jogadores devem ser informados em uma lista.")
        if not jogadores:
            raise ValueError("A lista de jogadores não pode estar vazia.")

        self.jogadores = jogadores.copy()
        self.baralho = baralho
        self.tabuleiro = tabuleiro
        self.carta_secreta = None

    def preparar_rodada(self) -> str:
        """Retira uma carta do baralho e a armazena para a rodada.

        Cada chamada retira uma carta. Se o baralho estiver vazio,
        propaga o ValueError de Baralho e mantém a carta anterior.
        """
        self.carta_secreta = self.baralho.puxar_carta()
        return self.carta_secreta
