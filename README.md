# Entre Linhas — Versão Terminal

Jogo de cartas cooperativo de dedução para terminal, baseado no jogo físico *Entre Linhas*
(PaperGames). Projeto desenvolvido para a disciplina C14 - Engenharia de Software (Inatel).

## Como funciona o jogo

O tabuleiro é uma grade de linhas (letras) e colunas (números). Cada carta cruza uma
palavra-linha com uma palavra-coluna. O jogador da vez recebe uma carta secreta e dá uma
dica de uma única palavra representando esse cruzamento; os demais jogadores tentam
adivinhar a coordenada correspondente. Acertando, a carta é posicionada no tabuleiro;
errando, é descartada. O objetivo é cooperativo: preencher o máximo possível da tabela.

## Tecnologias

- **Linguagem:** Python 3
- **Interface de terminal:** rich
- **Gerenciamento de dependências:** pip (`requirements.txt`)
- **Testes:** pytest
- **Banco de dados:** SQLite
- **CI/CD:** Jenkins

## Instalação

```bash
git clone <url-do-repositorio>
cd entre-linhas
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
python src/main.py
```

## Funcionalidades

- [ ] Iniciar partida com número configurável de jogadores
- [ ] Distribuição automática de cartas e montagem do tabuleiro
- [ ] Exibição da carta secreta ao jogador da vez
- [ ] Envio de dica e validação (uma única palavra)
- [ ] Tentativa de palpite de coordenada
- [ ] Atualização de tabuleiro e pontuação
- [ ] Histórico de dicas da partida
- [ ] Pontuação final
- [ ] Persistência de partidas em SQLite

## Testes

```bash
pytest
```

## Estrutura atual do projeto

```text
entre-linhas/
├── src/
│   └── __init__.py
├── tests/
│   └── test_setup.py
├── pytest.ini
├── requirements.txt
└── README.md
```
