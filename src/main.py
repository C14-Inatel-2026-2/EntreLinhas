from EntreLinhas.src.Baralho import Baralho

if __name__ == '__main__':
    linhas = ['A', 'B']
    colunas = ['1', '2']
    meu_baralho = Baralho(linhas, colunas)

    print("Baralho inicial:", meu_baralho.cartas)

    meu_baralho.embaralhar()
    print("Baralho embaralhado:", meu_baralho.cartas)

    mao = meu_baralho.distribuir(2)
    print("Cartas na mão:", mao)
    print("Cartas restantes no deck:", meu_baralho.cartas)