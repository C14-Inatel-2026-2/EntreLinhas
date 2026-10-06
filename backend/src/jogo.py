"""Preparação inicial da partida com jogadores, baralho e tabuleiro."""

from .Baralho import Baralho
from .tabuleiro import Tabuleiro


class Jogo:
    """Reúne as dependências que serão coordenadas pelas futuras regras.

    O baralho e o tabuleiro devem ser criados com as mesmas coordenadas
    da grade 5x5. As cartas e células permanecem sob responsabilidade
    dessas instâncias, sem cópias ou alterações durante a inicialização.
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
