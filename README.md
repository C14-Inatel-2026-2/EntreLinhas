# 🎴 Entre Linhas — Versão Web

> *Uma dica, muitas conexões.*

Jogo de cartas **cooperativo de dedução** para navegador, inspirado no jogo físico
*Entre Linhas* (PaperGames). Desenvolvido para a disciplina **C14 — Engenharia de
Software** do Inatel.

---

## 🎲 Como funciona o jogo

Entre Linhas é um jogo onde **todos jogam no mesmo time**. O objetivo é preencher
o máximo possível de um tabuleiro 5×5, conectando palavras por meio de dicas criativas.

### O tabuleiro

O tabuleiro é uma grade onde cada **linha** e cada **coluna** possuem uma
**palavra-tema** (por exemplo: *mar*, *viagem*, *música*, *festa*, *escola*).
Cada célula do tabuleiro é identificada por uma **coordenada** (ex: `A3`),
representando o cruzamento entre a palavra da linha e a palavra da coluna.

```
         1          2          3          4          5
      (praia)   (inverno)  (viagem)  (comida)   (festa)
A (mar)    .          .          .          .          .
B (sol)    .          .          .          .          .
C (amor)   .          .          .          .          .
D (casa)   .          .          .          .          .
E (livro)  .          .          .          .          .
```

### Fluxo de uma rodada

```
┌─────────────────────────────────────────────────────────┐
│  1. O jogador da vez recebe uma CARTA SECRETA           │
│     → A carta indica uma coordenada (ex: A3)            │
│     → Ele vê as duas palavras: "mar" (linha A)          │
│       e "viagem" (coluna 3)                             │
│                                                         │
│  2. Ele dá UMA ÚNICA DICA (uma palavra só)              │
│     → Exemplo: "cruzeiro" (conecta mar + viagem)        │
│                                                         │
│  3. Os DEMAIS jogadores discutem e escolhem             │
│     uma coordenada no tabuleiro                         │
│     → Clicam na célula que acham correta                │
│                                                         │
│  4. Resultado:                                          │
│     ✅ Acertou → a carta é posicionada no tabuleiro     │
│     ❌ Errou  → a carta é descartada                    │
│                                                         │
│  5. Próximo jogador recebe uma nova carta secreta       │
└─────────────────────────────────────────────────────────┘
```

### Objetivo

O jogo é **cooperativo** — não há vencedores ou perdedores individuais. O time
tenta preencher o maior número possível de células do tabuleiro. Quanto mais
acertos, melhor a pontuação final do grupo!

### Regras importantes

- A dica deve ser **uma única palavra**
- A dica **não pode** ser igual a nenhuma das palavras do tabuleiro
- O jogador que dá a dica **não participa** do palpite
- A partida aceita de **2 a 6 jogadores**
- Recomendado para **8+ anos**

---

## 🛠️ Tecnologias

| Camada         | Tecnologia                                            |
|----------------|-------------------------------------------------------|
| **Backend**    | Python 3, Flask                                       |
| **Frontend**   | HTML, CSS, JavaScript (vanilla — sem frameworks)      |
| **Banco**      | SQLite (via `sqlite3` nativo do Python)               |
| **Testes**     | pytest (Python) · Cypress + Mochawesome (interface)   |
| **Deps**       | pip (`requirements.txt`) · npm (`package.json`)       |
| **CI/CD**      | Jenkins *(pipeline previsto)*                         |

---

## 📦 Instalação

### Pré-requisitos

- **Python 3.9+**
- **Node.js 22, 24 ou 26+** (indicado em `.nvmrc`)

### Passo a passo

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd EntreLinhas

# 2. Crie e ative o virtualenv
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3. Instale as dependências Python
pip install -r requirements.txt

# 4. Instale as dependências Node.js (para os testes E2E)
npm ci

# 5. Inicialize o banco de dados
python3 -c "from db import conectar_bd, criar_tabelas; conn = conectar_bd(); criar_tabelas(conn); conn.close()"
```

> **💡 Dica:** O script `start.sh` faz tudo isso automaticamente!
> ```bash
> bash scripts/start.sh --install
> ```

---

## 🚀 Execução

### Usando os scripts (recomendado)

```bash
# Instalação completa + iniciar servidor
bash scripts/start.sh --install

# Apenas iniciar o servidor (se já instalou antes)
bash scripts/start.sh

# Modo rápido (sem banner, sem verificações)
bash scripts/run.sh
```

### Manualmente

```bash
source .venv/bin/activate
python3 -m http.server 8000 --bind 127.0.0.1 --directory static
```

Acesse **http://127.0.0.1:8000** no navegador.

---

## 🧪 Testes

### Testes E2E (Cypress)

Executam automaticamente o servidor, rodam os testes no navegador e geram um
relatório visual com Mochawesome:

```bash
npm run test:e2e
```

Abra `reports/cypress/index.html` para ver o relatório.

Para rodar no modo interativo (com a interface do Cypress):

```bash
npm run test:e2e:open
```

> Consulte o [guia dos testes Cypress](cypress/README.md) para cenários
> detalhados e limitações.

### Testes Python (pytest)

```bash
python3 -m pytest
```

---

## ✅ Funcionalidades

- [ ] Iniciar partida com número configurável de jogadores (2–6)
- [ ] Cadastro dos nomes dos jogadores
- [ ] Distribuição automática de cartas e montagem do tabuleiro 5×5
- [ ] Exibição da carta secreta ao jogador da vez
- [ ] Envio de dica (uma única palavra) com validação
- [ ] Palpite de coordenada pela equipe (seleção clicável no tabuleiro)
- [ ] Feedback visual de acerto/erro com atualização do tabuleiro
- [ ] Placar em tempo real (acertos × erros)
- [ ] Histórico de dicas da partida
- [ ] Tela de resultado final com pontuação
- [ ] Persistência de partidas e jogadas em SQLite
- [ ] Opção de jogar novamente

---

## 📁 Estrutura do projeto

```
EntreLinhas/
├── static/                  # Front-end web (SPA vanilla)
│   ├── index.html           # Página principal (telas do jogo)
│   ├── README.md            # Guia do front-end e contrato da API
│   ├── css/
│   │   ├── style.css        # Entrada dos estilos
│   │   ├── base/            # Variáveis, tipografia e acessibilidade
│   │   ├── layout/          # Estrutura compartilhada
│   │   ├── components/      # Controles, painéis, feedback, placar, tabuleiro
│   │   └── pages/           # Início, jogadores, jogo e resultado
│   └── js/
│       ├── app.js           # Lógica principal da SPA
│       ├── config.js        # Configurações da aplicação
│       ├── services/        # Comunicação com a API (api.js)
│       ├── ui/              # Componentes de interface (jogadores.js)
│       └── utils/           # Utilitários (dom.js, validacao.js)
├── src/                     # Back-end / lógica do jogo
│   ├── __init__.py
│   ├── Baralho.py           # Classe Baralho (criar, embaralhar, distribuir)
│   ├── main.py              # Ponto de entrada do jogo
│   └── tabuleiro.py         # Classe Tabuleiro (grade 5×5, coordenadas)
├── scripts/                 # Scripts de automação
│   ├── run.sh               # Iniciar servidor (modo rápido)
│   └── start.sh             # Setup completo + servidor
├── tests/                   # Testes Python
│   └── test_baralho.py
├── cypress/                 # Testes E2E do navegador
│   ├── e2e/                 # Especificações de teste
│   ├── fixtures/            # Dados de teste (contrato da API)
│   ├── support/             # Comandos customizados
│   └── README.md            # Guia dos testes Cypress
├── db.py                    # Conexão e schema SQLite
├── jogo.db                  # Banco de dados SQLite
├── requirements.txt         # Dependências Python
├── package.json             # Dependências Node.js
├── package-lock.json        # Lock das dependências Node.js
├── cypress.config.js        # Configuração do Cypress
├── pytest.ini               # Configuração do pytest
├── .env                     # Variáveis de ambiente
├── .nvmrc                   # Versão do Node.js
└── .gitignore
```

---

## 👥 Equipe

Projeto desenvolvido para a disciplina **C14 — Engenharia de Software** do
[Inatel](https://inatel.br).

---

<p align="center">
  Feito para pensar junto. ✦ <strong>Entre Linhas</strong>
</p>
