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
- **Gerenciamento de dependências:** pip (`backend/requirements.txt`) e npm (`frontend/package.json` e `frontend/package-lock.json`)
- **Testes:** pytest para Python; Cypress com relatório Mochawesome para a interface
- **Banco de dados:** SQLite
- **CI/CD:** Jenkins com job de deploy no Railway; integração de Build e Testes em andamento

## Instalação

Requisitos: Python 3.9+ e Node.js 24 (indicado em `frontend/.nvmrc`; o Cypress também aceita
Node.js 22 e 26+). Se usar nvm, execute `nvm install` e `nvm use` em `frontend/`.

```bash
git clone <url-do-repositorio>
cd entre-linhas
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

`backend/requirements.txt` reúne Flask e Gunicorn para a aplicação, e pytest e pytest-cov
para testes e cobertura.
SQLite já faz parte do Python. As dependências de teste da interface ficam no
`frontend/package.json`: Cypress, `cypress-mochawesome-reporter` e `start-server-and-test`,
com versões fixas e dependências transitivas registradas em `frontend/package-lock.json`.
Use `npm --prefix frontend ci` na raiz ao instalar o projeto a partir do repositório.

## Execução

```bash
cd backend
python3 -m flask --app app run --host 127.0.0.1 --port 5000
```

Abra `http://127.0.0.1:5000/static/index.html`. O Flask serve a interface e a API
na mesma origem. As partidas e jogadas são salvas no SQLite local (`backend/jogo.db` ao executar nessa pasta).

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

`IMAGE_TAG` permite identificar a imagem local pelo hash do commit. No Jenkins,
o pipeline único instala as dependências, testa backend e frontend e só então
permite publicar no Railway.

## Deploy Jenkins → Railway

O `Jenkinsfile` executa o deploy no próprio servidor Jenkins Linux, pelo executor
`built-in`. O servidor precisa de Git, Bash, Python 3, Node.js e Railway CLI
(`npm install -g @railway/cli@5.63.1`), além dos plugins Pipeline, Git e
Credentials Binding e JUnit. O serviço `jenkins` do Compose inclui Git, Python com pip/venv,
Node.js 24 e Railway CLI na imagem, preservando as ferramentas nas reconstruções.

```bash
docker volume create jenkins-entrelinhas-home
docker compose --profile ci up --build -d --wait jenkins
```

Acesse `http://localhost:8081`. O volume `jenkins-entrelinhas-home` preserva jobs,
plugins e credenciais e reaproveita os dados do Jenkins existente neste computador.
O perfil `ci` permite iniciar Jenkins independentemente dos serviços do jogo.
Para pará-lo, use `docker compose --profile ci stop jenkins`.
O volume do Jenkins é externo ao Compose; não é removido por `down -v`.
Evite esse comando para preservar também o volume SQLite do jogo.
Em outra máquina, a primeira execução exige configurar usuário, plugins e jobs.

O pipeline é único (um job): `Preparar commit` → `Build` →
`Testes de backend e cobertura` → `Frontend/Cypress - Mateus` → `Deploy - Fernando`.
O backend executa toda a suíte Python, incluindo jogo e baralho, uma única vez,
com JUnit e cobertura XML/HTML em `reports/backend/`. O stage do Mateus roda
unitários com cobertura e Cypress (mock e API real), com Flask e SQLite
temporários. Os relatórios e o log do Flask ficam em `frontend/reports/`,
arquivados mesmo em falha. O servidor e o banco de teste são descartados ao final.
A instalação de dependências ocorre apenas no stage Build.

`DEPLOY` vem **desmarcado**: assim é possível validar uma branch sem credenciais
Railway e sem publicar. Para publicar, marque-o; backend e frontend precisam
aprovar o mesmo SHA neste build. Falha, interrupção ou resultado instável bloqueia
a publicação. `COMMIT_SHA` vazio resolve uma única vez a ponta da `main`;
para validar esta branch, publique-a e informe seu SHA completo.

Após alterar `docker/Dockerfile.jenkins`, reconstrua a imagem com
`docker compose --profile ci up --build -d --wait jenkins`.
O Jenkins usa Chromium, Xvfb e bibliotecas do Cypress; o Compose reserva 1 GB de `/dev/shm`.

Crie o job Pipeline `EntreLinhas-Deploy`, selecione **Pipeline script**, copie
o conteúdo do `Jenkinsfile` e mantenha **Use Groovy Sandbox** ativado.
Ao alterar o arquivo, atualize também o script salvo no job.
Cadastre um Project Token do Railway como credencial **Secret text**, com ID
`railway-project-token`. Nunca coloque o token no Git ou nos parâmetros.

Em **Build with Parameters**, informe:

| Parâmetro | Valor |
| --- | --- |
| `COMMIT_SHA` | SHA completo de 40 caracteres a testar; vazio usa `main` |
| `DEPLOY` | Desmarcado: somente CI; marcado: testes e publicação |
| `RAILWAY_PROJECT_ID` | `67641175-19f1-4597-a518-3ddea95e22fa` |
| `RAILWAY_SERVICE` | `EntreLinhas`, ou ID do serviço |
| `RAILWAY_ENVIRONMENT` | `production`, ou ambiente associado ao token |
| `PUBLIC_URL` | `https://entrelinhas-production-7e6e.up.railway.app` |

O pipeline baixa o repositório, seleciona o SHA, instala dependências e executa
as suítes. Quando `DEPLOY` está marcado, publica com `railway up --ci` e espera
que `/static/release.json` informe o SHA testado, além de verificar `/health` e
`/static/index.html`. Isso impede aprovar apenas a versão anterior ainda no ar.
O marcador é um artefato temporário gerado pelo deploy, incluído na imagem e
removido do workspace ao final. O timeout global é 30 minutos.

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
- [x] Pop-up de acerto e erro após cada palpite
- [x] Nome de quem dá a dica e de quem confirma o palpite
- [x] Encerramento antecipado com preservação do placar
- [x] Atualização de tabuleiro e pontuação
- [x] Histórico de dicas da partida no banco de dados
- [x] Pontuação final
- [x] Persistência de partidas em SQLite

## Testes

Para executar os testes do navegador e gerar o relatório Mochawesome, com Node.js
22, 24 ou 26+ e Python 3 instalados:

```bash
npm --prefix frontend ci
npm --prefix frontend run test:e2e
```

Abra `frontend/reports/cypress/index.html` para visualizar o resultado. O servidor de testes
é iniciado e encerrado automaticamente. As respostas HTTP são controladas
pelo Cypress; essa suíte valida a interface,
não a integração com Python/SQLite. Consulte o [guia dos testes](frontend/cypress/README.md)
para os cenários, modo interativo e limitações.

Os testes Python existentes continuam separados:

```bash
cd backend
python3 -m pytest
```

## Estrutura atual do projeto

```text
entre-linhas/
├── backend/                 # API, banco e regras Python
│   ├── app.py
│   ├── db.py
│   ├── jogo.py
│   ├── src/                 # Classes de domínio
│   ├── tests/               # Testes Python
│   ├── pytest.ini
│   ├── requirements.txt     # Dependências Python
│   └── README.md
├── frontend/                # Interface e ferramentas JavaScript
│   ├── static/              # HTML, CSS e JavaScript
│   ├── tests/               # Testes unitários JavaScript
│   ├── cypress/             # Testes de navegador
│   ├── cypress.config.js
│   ├── package.json         # Dependências e comandos npm
│   ├── package-lock.json    # Versões transitivas fixadas
│   ├── .nvmrc
│   └── README.md
├── docker/                  # Infraestrutura dos containers
├── docs/                    # Documentação compartilhada
├── Dockerfile               # Backend e imagem integrada Railway
├── compose.yaml
├── Jenkinsfile
├── railway.json
└── README.md
```

Para executar e manter a interface web, consulte o [guia do front-end](frontend/README.md).
