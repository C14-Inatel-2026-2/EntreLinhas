# Entre Linhas — Versão Web

Jogo de cartas cooperativo de dedução para navegador, baseado no jogo físico *Entre Linhas*
(PaperGames). Projeto desenvolvido para a disciplina C14 - Engenharia de Software (Inatel).

## Como funciona o jogo

O tabuleiro é uma grade de linhas (letras) e colunas (números). Cada carta cruza uma
palavra-linha com uma palavra-coluna. O jogador da vez recebe uma carta secreta e dá uma
dica de uma única palavra representando esse cruzamento; os demais jogadores tentam
adivinhar a coordenada correspondente. Acertando, a carta é posicionada no tabuleiro;
errando, é descartada. O objetivo é cooperativo: preencher o máximo possível da tabela.

## Tecnologias

- **Linguagem:** Python 3
- **Interface web:** HTML, CSS e JavaScript vanilla
- **API:** Flask
- **Gerenciamento de dependências:** pip (`requirements.txt`) e npm (`package-lock.json`)
- **Testes:** pytest para Python; Cypress com relatório Mochawesome para a interface
- **Banco de dados:** SQLite
- **CI/CD previsto:** Jenkins (pipeline ainda não implementado)

## Instalação

Requisitos: Python 3.9+ e Node.js 24 (indicado em `.nvmrc`; o Cypress também aceita
Node.js 22 e 26+). Se usar nvm, execute `nvm install` e `nvm use` na raiz.

```bash
git clone <url-do-repositorio>
cd entre-linhas
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
npm ci
```

`requirements.txt` instala Flask para o backend web e pytest para os testes Python.
SQLite já faz parte do Python. As dependências de teste da interface ficam no
`package.json`: Cypress, `cypress-mochawesome-reporter` e `start-server-and-test`,
com versões fixas e dependências transitivas registradas em `package-lock.json`.
Use `npm ci` ao instalar o projeto a partir do repositório.

## Execução

```bash
python3 -m flask --app app run --host 127.0.0.1 --port 5000
```

Abra `http://127.0.0.1:5000/static/index.html`. O Flask serve a interface e a API
na mesma origem. As partidas e jogadas são salvas no SQLite local (`jogo.db`).

## Funcionalidades

- [x] Iniciar partida com número configurável de jogadores
- [x] Distribuição automática de cartas e montagem do tabuleiro
- [x] Exibição da carta secreta ao jogador da vez
- [x] Envio de dica e validação (uma única palavra)
- [x] Tentativa de palpite de coordenada
- [x] Atualização de tabuleiro e pontuação
- [x] Histórico de dicas da partida no banco de dados
- [x] Pontuação final
- [x] Persistência de partidas em SQLite

## Testes

Para executar os testes do navegador e gerar o relatório Mochawesome, com Node.js
22, 24 ou 26+ e Python 3 instalados:

```bash
npm ci
npm run test:e2e
```

Abra `reports/cypress/index.html` para visualizar o resultado. O servidor de testes
é iniciado e encerrado automaticamente. As respostas HTTP são controladas
pelo Cypress; essa suíte valida a interface,
não a integração com Python/SQLite. Consulte o [guia dos testes](cypress/README.md)
para os cenários, modo interativo e limitações.

Os testes Python existentes continuam separados:

```bash
python3 -m pytest
```

## Estrutura atual do projeto

```text
entre-linhas/
├── static/                # Front-end web (SPA vanilla)
│   ├── index.html
│   ├── README.md          # Guia de execução e contrato da API
│   ├── css/
│   │   ├── style.css      # Entrada dos estilos
│   │   ├── base/          # Variáveis, tipografia e acessibilidade
│   │   ├── layout/        # Estrutura compartilhada
│   │   ├── components/    # Controles, painéis, feedback, placar e tabuleiro
│   │   └── pages/         # Início, jogadores, jogo e resultado
│   └── js/
│       ├── app.js
│       ├── config.js
│       ├── services/
│       ├── ui/
│       └── utils/
├── src/
│   ├── __init__.py
│   ├── Baralho.py
│   ├── main.py
│   └── tabuleiro.py
├── tests/
│   └── test_baralho.py
├── cypress/               # Testes e dados de contrato exclusivos da suíte
│   ├── e2e/
│   ├── fixtures/
│   ├── support/
│   └── README.md
├── cypress.config.js
├── package.json
├── package-lock.json
├── db.py
├── pytest.ini
├── requirements.txt
└── README.md
```

Para executar e manter a interface web, consulte o [guia do front-end](static/README.md).
