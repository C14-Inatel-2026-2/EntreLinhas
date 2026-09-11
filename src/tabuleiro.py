class Tabuleiro:
    def __init__(self, topicos_linhas: list[str], topicos_colunas: list[str]):
        # Define os 5 tópicos das linhas e os 5 tópicos das colunas (totalizando 5x5 para as cartas)
        self.linhas = topicos_linhas[:5]
        self.colunas = topicos_colunas[:5]
        
        # Cria a grade interna de 5x5 para guardar o estado das cartas jogadas (inicialmente vazia com None)
        self.grade = [[None for _ in range(5)] for _ in range(5)]

    def coordenada_valida(self, coordenada: str) -> bool:
        """Verifica se uma coordenada no formato ex: 'A3' é válida dentro do tabuleiro."""
        if not isinstance(coordenada, str) or len(coordenada) < 2:
            return False
        
        linha = coordenada[0].upper()
        coluna = coordenada[1:]
        
        return linha in self.linhas and coluna in self.colunas

    def exibir(self):
        """Exibe o tabuleiro 6x6 no terminal (cabeçalhos + grade 5x5)."""
        # A primeira linha exibe um espaço vazio no canto superior esquerdo ([0][0]) seguido dos tópicos das colunas
        cabecalho = [" "] + self.colunas
        print(" | ".join(cabecalho))
        print("-" * 25)
        
        # Para cada linha, exibe o tópico da linha seguido do estado de cada uma das 5 colunas
        for i, linha_topico in enumerate(self.linhas):
            # Se a célula estiver vazia (None), mostra '.', senão mostra o estado da carta
            linha_valores = [
                str(self.grade[i][j]) if self.grade[i][j] is not None else "." 
                for j in range(5)
            ]
            linha_atual = [linha_topico] + linha_valores
            print(" | ".join(linha_atual))