import random


class Baralho:
    def __init__(self, palavras_linha, palavras_coluna):
        self.cartas = [f"{linha}-{coluna}" for linha in palavras_linha for coluna in palavras_coluna]

    def embaralhar(self):
        random.shuffle(self.cartas)

    def distribuir(self, quantidade):
        if quantidade > len(self.cartas):
            raise ValueError("Não há cartas suficientes no baralho para distribuir.")

        mao = self.cartas[:quantidade]
        self.cartas = self.cartas[quantidade:]
        return mao