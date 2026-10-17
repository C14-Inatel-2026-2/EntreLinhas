import random


class Baralho:
    def __init__(self, palavras_linha, palavras_coluna):
        if not palavras_linha or  not palavras_coluna:
            raise ValueError("As listas de linhas e colunas não podem estar vazias.")

        self.cartas = [
            f"{str(linha).upper()}{str(coluna)}"
            for linha in palavras_linha
            for coluna in palavras_coluna
        ]

    def embaralhar(self):
        random.shuffle(self.cartas)

    def distribuir(self, quantidade: int):
        if not isinstance(quantidade, int) or quantidade <= 0:
            raise ValueError("A quantidade de cartas a distribuir deve ser um número inteiro positivo.")

        if quantidade > len(self.cartas):
            raise ValueError("Não há cartas suficientes no baralho para distribuir.")

        mao = self.cartas[:quantidade]
        self.cartas = self.cartas[quantidade:]
        return mao

    def __len__(self) -> int:
        return len(self.cartas)

    def esta_vazio(self) -> bool:
        """Verifica se o baralho não possui mais cartas."""
        return len(self.cartas) == 0

    def puxar_carta(self) -> str:
        """Retira e retorna uma única carta do topo do baralho."""
        return self.distribuir(1)[0]
