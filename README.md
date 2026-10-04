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
- **CI/CD:** Jenkins com job de deploy no Railway; integração de Build e Testes em andamento

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

`requirements.txt` reúne Flask e Gunicorn para a aplicação, e pytest e pytest-cov
para testes e cobertura.
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

## Docker

Para volumes, testes em containers e deploy no Railway, consulte
[Docker e Railway](docs/docker-railway.md).

Com Docker Desktop iniciado e configurado para containers Linux, execute na raiz:

```bash
docker compose up --build -d --wait
```

Abra `http://localhost:8080`. O Compose executa frontend Nginx e backend
Gunicorn em containers separados. O Nginx encaminha a API ao backend. Node e
Cypress ficam fora da imagem de execução; os testes devem rodar nos jobs de CI.

```bash
docker compose ps
docker compose logs -f backend frontend
docker compose down
```

O SQLite fica no volume `jogo-data`, em `/data/jogo.db`, e permanece após
`docker compose down` e reconstruções da imagem. O banco local existente não é
copiado para o container: a primeira execução começa com um banco vazio.
Não use `docker compose down -v` se quiser manter as partidas.

A porta é publicada apenas no computador local. Para mudar a porta no PowerShell:

```powershell
$env:APP_PORT = "8000"
docker compose up --build -d --wait
```

O job Build do Jenkins poderá executar `docker compose build`. `IMAGE_TAG`
permite identificar a imagem pelo hash do commit. A integração dos jobs de
Build e Testes com o Deploy ainda deve ser concluída.

## Deploy Jenkins → Railway

O `Jenkinsfile` executa o deploy no próprio servidor Jenkins Linux, pelo executor
`built-in`. O servidor precisa de Git, Bash, Python 3, Node.js e Railway CLI
(`npm install -g @railway/cli@5.63.1`), além dos plugins Pipeline, Git e
Credentials Binding. Se o container Jenkins for recriado, reinstale essas ferramentas.

Crie o job Pipeline `EntreLinhas-Deploy`, selecione **Pipeline script**, copie
o conteúdo do `Jenkinsfile` e mantenha **Use Groovy Sandbox** ativado.
Ao alterar o arquivo, atualize também o script salvo no job.
Cadastre um Project Token do Railway como credencial **Secret text**, com ID
`railway-project-token`. Nunca coloque o token no Git ou nos parâmetros.

Em **Build with Parameters**, informe:

| Parâmetro | Valor |
| --- | --- |
| `COMMIT_SHA` | SHA completo de 40 caracteres aprovado em Build e Testes |
| `RAILWAY_PROJECT_ID` | `67641175-19f1-4597-a518-3ddea95e22fa` |
| `RAILWAY_SERVICE` | `EntreLinhas`, ou ID do serviço |
| `RAILWAY_ENVIRONMENT` | `production`, ou ambiente associado ao token |
| `PUBLIC_URL` | `https://entrelinhas-production-7e6e.up.railway.app` |

O pipeline baixa a branch `main`, seleciona o SHA informado, publica com
`railway up` e verifica `/health` e `/static/index.html`. O timeout é 30 minutos.
Este job executa somente Deploy; a integração deve acioná-lo após Build e Testes
aprovados, passando o mesmo SHA. Restrinja o acionamento manual conforme as
permissões do grupo.

No Railway, use o `Dockerfile` da raiz, uma réplica, healthcheck `/health`,
volume montado em `/data`, `DATABASE_PATH=/data/jogo.db` e `RAILWAY_RUN_UID=0`.
Use a variável `PORT` fornecida pelo Railway e mantenha o Start Command padrão:
o entrypoint prepara o volume e inicia o Gunicorn com privilégios reduzidos.
Desative o autodeploy para deixar a publicação sob controle do Jenkins.
O Dockerfile instala dependências com `pip --no-cache-dir`, sem cache mounts
que dependam do ID de um serviço Railway.

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
