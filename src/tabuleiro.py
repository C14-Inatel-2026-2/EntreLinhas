class Tabuleiro:
    def __init__(self, topicos_linhas: list[str], topicos_colunas: list[str]):
        # Garante exatamente 5 tópicos para linhas e 5 para colunas
        self.linhas = [str(l).upper() for l in topicos_linhas[:5]]
        self.colunas = [str(c) for c in topicos_colunas[:5]]
        
        # Grade interna 5x5 para armazenar o estado das cartas jogadas (inicialmente None)
        self.grade = [[None for _ in range(5)] for _ in range(5)]

    def coordenada_valida(self, coordenada: str) -> bool:
        """Verifica se uma coordenada no formato ex: 'A3' é válida dentro do tabuleiro."""
        if not isinstance(coordenada, str) or len(coordenada) < 2:
            return False
        
        linha = coordenada[0].upper()
        coluna = coordenada[1:]
        
        return linha in self.linhas and coluna in self.colunas

    def _obter_indices(self, coordenada: str):
        """Converte uma coordenada string (ex: 'A1') em índices numéricos da matriz (linha, coluna)."""
        if not self.coordenada_valida(coordenada):
            raise ValueError(f"Coordenada inválida: {coordenada}")
        
        linha_letra = coordenada[0].upper()
        coluna_num = coordenada[1:]
        
        i = self.linhas.index(linha_letra)
        j = self.colunas.index(coluna_num)
        return i, j

    def registrar_jogada(self, coordenada: str, carta) -> bool:
        """Registra uma carta em uma coordenada válida se ela estiver vazia."""
        i, j = self._obter_indices(coordenada)
        
        if self.grade[i][j] is not None:
            return False  # A casa já está ocupada
            
        self.grade[i][j] = carta
        return True

    def exibir(self):
        """Exibe o tabuleiro 6x6 no terminal (cabeçalhos de tópicos + grade 5x5)."""
        # A primeira linha exibe um espaço vazio no canto superior esquerdo ([0][0]) seguido dos tópicos das colunas
        cabecalho = [" "] + self.colunas
        print(" | ".join(cabecalho))
        print("-" * 25)
        
        # Para cada linha, exibe o tópico da linha seguido do estado de cada uma das 5 colunas
        for i, linha_topico in enumerate(self.linhas):
            linha_valores = [
                str(self.grade[i][j]) if self.grade[i][j] is not None else "." 
                for j in range(5)
            ]
            linha_atual = [linha_topico] + linha_valores
            print(" | ".join(linha_atual))