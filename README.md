# Entre Linhas — Versão Web

Jogo de cartas cooperativo de dedução para navegador, baseado no jogo físico *Entre Linhas*
(PaperGames). Projeto desenvolvido para a disciplina C14 - Engenharia de Software (Inatel).

## Navegação

- [Como funciona o jogo](#como-funciona-o-jogo)
- [Instalação](#instalação) e [execução](#execução)
- [Arquitetura e API](#arquitetura-e-api)
- [Docker](#docker) e [Jenkins/Railway](#deploy-jenkins--railway)
- [Funcionalidades](#funcionalidades) e [testes](#testes)
- [Histórias de usuário](#histórias-de-usuário)
- [Metodologia de desenvolvimento](#metodologia-de-desenvolvimento)
- [Dinâmica de desenvolvimento e refatorações](#dinâmica-de-desenvolvimento-e-refatorações)
- [Uso de IA](#uso-de-ia)
- [Pendências para a NP2](#pendências-para-a-np2)

## Como funciona o jogo

O tabuleiro é uma grade de linhas (letras) e colunas (números). Cada carta cruza uma
palavra-linha com uma palavra-coluna. O jogador da vez recebe uma carta secreta e dá uma
dica de uma única palavra representando esse cruzamento; os demais jogadores tentam
adivinhar a coordenada correspondente. Acertando, a carta é posicionada no tabuleiro;
errando, é descartada. O objetivo é cooperativo: preencher o máximo possível da tabela.

A versão web atual usa uma grade 3 × 3 (A–C e 1–3), nove cartas e de dois a seis
jogadores no mesmo navegador. Cada partida sorteia seis palavras distintas de um
catálogo de 200 palavras no SQLite. As palavras permanecem fixas durante a partida.

Para jogar:

1. Informe a quantidade de jogadores e os nomes na interface.
2. O jogador da vez consulta a carta secreta e envia uma dica de uma palavra.
3. Os demais combinam um palpite e selecionam a coordenada no tabuleiro.
4. Confira o feedback de acerto ou erro e acompanhe a troca de turno e o placar.
5. Complete as nove rodadas ou encerre antecipadamente, preservando o resultado.

## Tecnologias

- **Linguagem:** Python 3
- **Interface web:** HTML, CSS e JavaScript vanilla
- **API:** Flask
- **Gerenciamento de dependências:** pip (`backend/requirements.txt`) e npm (`frontend/package.json` e `frontend/package-lock.json`)
- **Testes:** pytest para Python; Cypress com relatório Mochawesome para a interface
- **Banco de dados:** SQLite
- **CI/CD:** Jenkins com testes, relatórios, cobertura e deploy automático no Railway após alterações na `main`

## Instalação

Requisitos: Python 3.9+ e Node.js 24 (indicado em `frontend/.nvmrc`; o Cypress também aceita
Node.js 22 e 26+). Se usar nvm, execute `nvm install` e `nvm use` em `frontend/`.

```bash
git clone https://github.com/C14-Inatel-2026-2/EntreLinhas.git
cd EntreLinhas
python3 -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

No Windows/PowerShell:

```powershell
git clone https://github.com/C14-Inatel-2026-2/EntreLinhas.git
cd EntreLinhas
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
```

Quem já clonou o repositório deve começar pela criação/ativação do ambiente virtual.
Node/npm são necessários para os testes de frontend; para jogar localmente basta
instalar as dependências Python e iniciar o Flask.

`backend/requirements.txt` reúne Flask e Gunicorn para a aplicação, e pytest e pytest-cov
para testes e cobertura.
SQLite já faz parte do Python. As dependências de teste da interface ficam no
`frontend/package.json`: Cypress, `cypress-mochawesome-reporter` e `start-server-and-test`,
com versões fixas e dependências transitivas registradas em `frontend/package-lock.json`.
Use `npm --prefix frontend ci` na raiz ao instalar o projeto a partir do repositório.

## Execução

```bash
cd backend
python -m flask --app app run --host 127.0.0.1 --port 5000
```

Abra `http://127.0.0.1:5000/static/index.html`. O Flask serve a interface e a API
na mesma origem. As partidas e jogadas são salvas no SQLite local (`backend/jogo.db` ao executar nessa pasta).

Encerre o servidor com `Ctrl+C`. Para usar outro arquivo SQLite, defina
`DATABASE_PATH` antes de iniciar o Flask; o diretório de destino deve existir e
permitir escrita. `/health` retorna HTTP 200 quando o banco está disponível e 503
quando a verificação falha.

## Arquitetura e API

O navegador carrega HTML/CSS/JavaScript e envia requisições JSON à API Flask.
O backend valida as fases da partida, aplica as regras e salva os dados em SQLite.
Na execução local, Flask serve também os arquivos estáticos; no Compose, Nginx
serve o frontend e encaminha as chamadas ao backend.

| Componente | Responsabilidade |
| --- | --- |
| `frontend/static/js/app.js` | Fluxo de telas, turnos, feedback e interação com a partida |
| `frontend/static/js/services/api.js` | Comunicação HTTP com a API |
| `backend/app.py` | Rotas, validações e coordenação das operações |
| `backend/jogo.py` | Montagem do estado retornado à interface e cartas da partida |
| `backend/db.py` | Inicialização, consultas e persistência SQLite |
| `backend/palavras.py` | Catálogo inicial de palavras |
| `backend/src/` | Classes de domínio e execução de terminal; a API usa também `backend/jogo.py` |

| Método e rota | Entrada / resultado |
| --- | --- |
| `GET /` | Redireciona para a interface |
| `GET /health` | Disponibilidade da aplicação e do banco |
| `POST /partida` | `{"num_jogadores": 2}`; cria partida e devolve o estado (201) |
| `GET /partida/<id>` | Dados cadastrais e resultado da partida; não retorna o estado completo da interface |
| `POST /partida/<id>/dica` | `{"dica": "ponte"}`; muda da fase de dica para palpite |
| `POST /partida/<id>/palpite` | `{"palpite": "A1"}`; registra a jogada e atualiza turno e placar |
| `GET /partida/<id>/placar` | Totais de acertos e erros |
| `POST /partida/<id>/encerrar` | Encerra antecipadamente e retorna o estado final |

As rotas de jogo retornam 400 para entradas inválidas, 404 para partidas
inexistentes e 409 para operações incompatíveis com a fase atual. A dica aceita
uma palavra de até 60 caracteres. O estado enviado durante a fase de palpite
oculta a carta secreta. A aplicação foi projetada para uso cooperativo no mesmo
navegador; não implementa salas online com autenticação e isolamento por jogador.

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
`Testes de jogo e baralho - Caio` → `Backend e cobertura - Henrique` →
`Frontend/Cypress - Mateus` → `Deploy - Fernando`.
Os testes Python são divididos sem duplicação: jogo e baralho no stage do Caio,
com relatórios em `reports/domain/`, e os demais casos no stage do Henrique,
com JUnit e cobertura XML/HTML em `reports/backend/`. A cobertura final agrega
as duas execuções. O stage do Mateus roda
unitários com cobertura e Cypress (mock e API real), com Flask e SQLite
temporários. Os relatórios e o log do Flask ficam em `frontend/reports/`,
arquivados mesmo em falha. O servidor e o banco de teste são descartados ao final.
A instalação de dependências ocorre apenas no stage Build.

O job consulta a `main` a cada dois minutos com `pollSCM('H/2 * * * *')`.
Quando detecta uma revisão nova, executa todos os stages e publica automaticamente
somente se tudo passar. A consulta exige que o computador, Docker e Jenkins
estejam ligados e com internet. Não precisa de webhook público nem GitHub Actions.
Sem alteração no repositório, a consulta não inicia outro build. Commits feitos
somente em branches de trabalho não publicam; aprovação e merge das PRs continuam
sob controle dos integrantes.

Em acionamentos automáticos, o Jenkins usa a ponta da `main`, resolvida uma única
vez, e ignora `COMMIT_SHA` ou `DEPLOY` de execuções manuais anteriores.
Em acionamentos **manuais**, `DEPLOY` continua desmarcado por padrão para permitir
validar uma branch sem publicar. Marque-o somente quando quiser publicar nessa
execução. Todos os stages precisam aprovar o mesmo SHA; falhas, interrupções ou
resultado instável bloqueiam a publicação.

Após alterar `docker/Dockerfile.jenkins`, reconstrua a imagem com
`docker compose --profile ci up --build -d --wait jenkins`.
O Jenkins usa Chromium, Xvfb e bibliotecas do Cypress; o Compose reserva 1 GB de `/dev/shm`.
O heap Java fica limitado a 384 MB e pode ser ajustado com `JENKINS_JAVA_OPTS`.
Recomenda-se reservar ao menos 4 GB de RAM ao Docker para Jenkins e navegador,
conforme os [requisitos de CI do Cypress](https://docs.cypress.io/app/get-started/install-cypress#Hardware).
Evite executar vários controladores Jenkins ao mesmo tempo em VMs pequenas.

Crie o job Pipeline `EntreLinhas-Deploy`, selecione **Pipeline script**, copie
o conteúdo do `Jenkinsfile` e mantenha **Use Groovy Sandbox** ativado.
Ao alterar o arquivo, atualize também o script salvo no job.
Cadastre um Project Token do Railway como credencial **Secret text**, com ID
`railway-project-token`. Nunca coloque o token no Git ou nos parâmetros.

Em **Build with Parameters**, informe:

| Parâmetro | Valor |
| --- | --- |
| `COMMIT_SHA` | SHA completo de 40 caracteres a testar; vazio usa `main` |
| `DEPLOY` | Execução manual: desmarcado = somente CI; marcado = testes e publicação. Polling da main publica automaticamente após os testes. |
| `RAILWAY_PROJECT_ID` | `67641175-19f1-4597-a518-3ddea95e22fa` |
| `RAILWAY_SERVICE` | `EntreLinhas`, ou ID do serviço |
| `RAILWAY_ENVIRONMENT` | `production`, ou ambiente associado ao token |
| `PUBLIC_URL` | `https://entrelinhas-production-7e6e.up.railway.app` |

O pipeline baixa o repositório, seleciona o SHA, instala dependências e executa
as suítes. Quando acionado pelo polling, ou manualmente com `DEPLOY` marcado,
publica com `railway up --ci` e espera
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
- [x] Sorteio de palavras do banco sem repetição na mesma partida
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

Para executar os unitários JavaScript na raiz:

```bash
npm --prefix frontend run test:unit
```

No Windows, use `npm --prefix frontend run test:e2e:windows` para os testes de
navegador com API simulada. O pipeline executa também a suíte com API real, por
`scripts/ci/frontend.py`, que depende de Linux, Gunicorn e controle de processos
POSIX. Veja os [resultados históricos de integração](docs/ci-integracao-validacao.md)
e a [configuração de CI automático](docs/ci-automatica.md).

Para gerar cobertura e relatórios Python, a partir de `backend/`:

```bash
python -m pytest tests --cov=app --cov=db --cov=jogo --cov=palavras --cov=src --cov-report=term-missing --cov-report=html:../reports/backend/htmlcov --junitxml=../reports/backend/junit.xml
```

Abra `reports/backend/htmlcov/index.html` para a cobertura. O JUnit é consumido
pelo Jenkins; os artefatos de cada execução ficam arquivados no build. Contagens
de testes e percentuais registrados em documentos históricos correspondem ao
commit daquela execução e devem ser regenerados para a entrega final.

## Histórias de usuário

As histórias de usuário estão **pendentes do envio de cada integrante**.
Serão incluídas após serem criadas pelos próprios autores como issues e
vinculadas ao [Projects do grupo](https://github.com/orgs/C14-Inatel-2026-2/projects/3).

Conforme a organização do quadro, Caio, Henrique e Mateus devem criar uma história
cada, e Fernando deve criar duas, totalizando cinco. Cada história deve conter
“Como…, quero…, para…”, critérios de aceitação verificáveis, prioridade, status
final e vínculos com PRs e testes pertinentes. Os cards de organização da entrega
não substituem essas histórias.

O envio é acompanhado pelas tarefas
[#48 — Caio](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/48),
[#49 — Henrique](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/49),
[#50 — Mateus](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/50) e
[#51 — Fernando](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/51),
com prazo em **31/10/2026**.

### US02 — Registrar um palpite (Henrique Rodrigues)

Como jogador, quero registrar meu palpite para descobrir se acertei e acompanhar minha pontuação.

- **Issue vinculada:** [#52](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/52)
- **Status:** Concluído
- **Evidências:** PRs [#3](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/3), [#18](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/18) e [#44](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/44)

#### Requisitos Funcionais (API e Placar)
- **RF-API-01 (Registro e Validação):** A API Flask disponibiliza o endpoint `POST /partida/<id>/palpite` para receber, validar a opção selecionada e registrar a jogada.
- **RF-API-02 (Feedback e Pontuação):** O retorno da requisição informa se o palpite foi correto ou incorreto e atualiza o placar e os turnos da partida de acordo com as regras do jogo.

#### Requisitos Não-Funcionais (Persistência)
- **RNF-PER-01 (Persistência em SQLite):** As jogadas, dados da partida e o histórico do placar são persistidos de forma síncrona no banco de dados SQLite (`jogo.db`).
- **RNF-PER-02 (Tratamento de Erros e Integridade):** A API trata requisições inválidas, fora de turno ou com parâmetros incorretos retornando status HTTP 4xx (como 400 ou 409) sem comprometer a integridade do banco de dados.

## Metodologia de desenvolvimento

O grupo utiliza **Kanban no GitHub Projects** para visualizar o andamento,
distribuir responsabilidades e acompanhar as entregas. O quadro
[EntreLinhas — Entrega 31/10/2026 — Kanban e documentação](https://github.com/orgs/C14-Inatel-2026-2/projects/3)
centraliza issues, responsáveis, prioridades e prazos. Essa organização permite
acompanhar o fluxo contínuo das tarefas e identificar pendências de implementação,
documentação e revisão.

O fluxo do quadro é **A fazer → Fazendo → Em revisão → Concluído**:

| Coluna | Etapa do trabalho |
| --- | --- |
| A fazer | Tarefa registrada, aguardando início pelo responsável |
| Fazendo | Implementação ou documentação em andamento |
| Em revisão | Contribuição aguardando conferência de outro integrante |
| Concluído | Entrega finalizada, com as evidências correspondentes |

Os campos de prioridade de execução e ordem de implementação ajudam a distinguir
as entregas prioritárias das melhorias adiadas. As issues detalham o trabalho e
seus vínculos com PRs; as branches isolam as alterações, e o Jenkins valida o
código integrado em `main`.

Para a entrega de 31/10, o Projects distribui também documentação e revisão:

| Integrante | Contribuição no README | Revisar contribuição de |
| --- | --- | --- |
| Caio | Requisitos funcionais das regras, turnos e dicas | Henrique |
| Henrique | Requisitos funcionais da API/placar e não funcionais de persistência | Mateus |
| Mateus | Descrição da aplicação, público e requisitos de interface/responsividade | Fernando |
| Fernando | Método Kanban, links das histórias, requisitos de execução/CI/CD e consolidação | Caio |

O critério de conclusão registrado no quadro exige cinco histórias com autoria
dos quatro integrantes, README com descrição e requisitos funcionais e não
funcionais, participação de todos em documentação e revisão e links das issues/PRs
como evidência. As PRs devem ser aprovadas por outra pessoa; somente o líder envia
o link ao professor.

Além dessa divisão, o histórico registra as seguintes entregas técnicas:

| Integrante | Entregas identificáveis no repositório |
| --- | --- |
| Caio Rodrigues | Baralho, regras de domínio e stage de jogo/baralho; PRs #2 e #42 |
| Henrique Rodrigues Mendonça | SQLite, API Flask e stage de backend/cobertura; PRs #3, #18 e #44 |
| Mateus Mendonça | Tabuleiro e stage de frontend/Cypress; PRs #1, #16 e #45 |
| Fernando Puebla Stein | Interface, integração, Docker, deploy e automação Jenkins; PRs #4, #25, #40, #46 e #47 |

Essa tabela descreve entregas técnicas; não atribui papéis de PO, facilitador ou
QA que não estejam confirmados pelos integrantes.

Proposta de definição de preparado (DoR), a ser acordada: issue com objetivo,
critério de aceitação, responsável e dependências identificadas.

Proposta de definição de pronto (DoD), a ser acordada: implementação e testes
pertinentes, documentação atualizada, revisão por outro integrante e execução
do pipeline para o commit integrado. O pipeline atual valida a `main` após o
merge; não constitui um check obrigatório de PR antes do merge.

Para completar as evidências do processo, registrar a frequência real de revisão
do quadro e das reuniões e pelo menos uma métrica com período e fonte (por
exemplo, issues concluídas por semana ou tempo entre abertura e merge de PRs).
Não há métricas calculadas nesta versão.

## Dinâmica de desenvolvimento e refatorações

O fluxo documentado em [CI automático](docs/ci-automatica.md) orienta criar uma
branch, enviar commits, abrir PR para `main` e solicitar revisão de outro membro.
Após o merge, Jenkins consulta a branch, testa um SHA fixo e só publica se todos
os stages o aprovarem. O padrão de commits observado inclui `feat:`, `fix:`,
`test:`, `refactor:`, `ci:` e `docs:`; o histórico não aplica esse padrão de
forma uniforme.

Exemplos concretos para discutir na defesa:

- **Organização do projeto:** a [PR #40](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/40)
  separou backend e frontend, agrupando código, dependências e testes por área.
- **Integração do pipeline:** a revisão da [PR #45](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/45)
  apontou que a mudança removia a execução de testes Python. A integração
  posterior preservou as suítes antes do deploy; a [PR #46](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/46)
  reúne os ajustes e a validação.
- **Correção de caminho:** a [PR #44](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/44)
  recebeu revisão sobre o caminho da virtualenv dentro de `backend/`, seguido
  de correção e aprovação.
- **Execução em CI:** os [registros de validação](docs/ci-integracao-validacao.md)
  descrevem limitações de memória, seleção do navegador e limpeza de processos
  e bancos temporários após falhas.

O grupo ainda deve complementar este relato com as decisões tomadas nas
reuniões, como redistribuiu tarefas diante de bloqueios e suas próprias lições
aprendidas. Os exemplos acima são evidências técnicas, não depoimentos dos membros.

## Uso de IA

Esta seção está em construção. É necessário reunir os relatos de todos os
integrantes antes da entrega, incluindo ferramentas/modelos efetivamente usados,
finalidade, prompts reais, avaliação das respostas e trabalho manual.

O grupo utilizou **GPT-6 e GPT-6.1 no Codex**, conforme declaração do integrante
responsável por esta atualização. A ferramenta auxiliou na análise de requisitos,
consulta de código, histórico e PRs, execução de testes e elaboração da documentação.
Os usos específicos dos demais integrantes ainda devem ser consolidados.

### Skills utilizadas

Skills são instruções especializadas que orientam o agente em tarefas específicas.
Seu uso complementa o modelo e deve ser declarado conforme as tarefas realizadas.

| Skill | Finalidade no projeto |
| --- | --- |
| `pdf:pdf` | Leitura e extração do documento Projeto C14 NP2 para comparar os requisitos com o código, testes, pipeline e documentação do repositório. |
| `frontend-design` | Apoio ao design e à organização visual da interface web. |
| `docker-project-foundations` | Apoio à organização da infraestrutura Docker do projeto. |
| `docker-build-strategies` | Orientação na estruturação dos Dockerfiles e das imagens da aplicação e do Jenkins. |
| `docker-compose-patterns` | Apoio à configuração dos serviços, volumes e comunicação entre containers no Docker Compose. |

O uso das skills de frontend e Docker foi informado pelo integrante responsável
por esta documentação; o uso de PDF foi acompanhado nesta revisão. A lista reúne
as principais skills declaradas e pode ser complementada com os relatos dos
demais integrantes.

### Exemplos de prompts para a IA CLI

Os três exemplos abaixo foram selecionados dos pedidos utilizados pelo grupo,
conforme relato do integrante responsável. São resumos dos prompts, sem pretensão
de reproduzir literalmente o texto enviado à ferramenta.

| Exemplo | Pedido à IA | Aplicação ou resultado relatado |
| --- | --- | --- |
| Frontend inicial | Criar o frontend em HTML/CSS/JavaScript vanilla, com tema cartoon, paleta inspirada no jogo, telas de início, jogo e resultado e consumo da API Flask. | Apoio à implementação da interface e à comunicação com o backend. A interface entregue pode ser consultada em `frontend/static/`. |
| Acompanhamento da evolução | Comparar o repositório com as issues #6 a #13, os testes por pessoa (com mock, sem mock e negativo), os commits e o equilíbrio das contribuições. | A análise apontou lógica de jogo duplicada e divergência entre o tabuleiro 5 × 5 e o jogo web 3 × 3. Essas pendências estão acompanhadas nas issues [#8](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/8) e [#14](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/14). |
| Atualização do GitHub Projects | Criar e atualizar as issues do pipeline de CI/CD, registrando o status real das entregas por pessoa. | Apoio à organização das tarefas e responsabilidades no [quadro Kanban](https://github.com/orgs/C14-Inatel-2026-2/projects/3), com vínculos entre issues, PRs e evidências de execução. |

Para cada exemplo, os integrantes ainda devem registrar quais respostas foram
aceitas, ajustadas ou descartadas e por quê, incluindo os vínculos com as alterações
correspondentes. Os resultados acima não substituem esse relato de revisão humana.

Também falta registrar a dinâmica de uso (individual, em dupla, revisão de PRs,
geração de testes etc.) e quais partes cada integrante desenvolveu manualmente.
A existência de um commit de autoria humana não comprova ausência de auxílio de IA.

## Pendências para a NP2

- [ ] Receber as histórias de cada integrante e consolidar links, critérios, prioridades, status e rastreabilidade.
- [ ] Complementar as evidências do Kanban no Projects com frequência de acompanhamento, reuniões e métricas reais.
- [ ] Completar o relato da dinâmica e das lições aprendidas pelos integrantes.
- [ ] Completar “Uso de IA” com todos os membros, três prompts reais e decisões sobre as respostas.
- [ ] Conferir com o professor a exigência de um **job por integrante**: o Jenkinsfile atual tem um único job com stages por integrante.
- [ ] Ampliar e evidenciar a participação dos membros nas revisões de PRs.
- [ ] Executar o pipeline no SHA final e apresentar os relatórios daquela versão.
- [ ] Preparar todos os integrantes para demonstrar código, testes, commits, PRs e decisões em uma defesa Q&A de até 20 minutos.

Limitações técnicas já acompanhadas: unificação/documentação das regras entre
`backend/jogo.py` e `backend/src/jogo.py` ([issue #8](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/8)),
transações e recuperação completa do estado ([issue #9](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/9))
e validação após essa integração ([issue #13](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/13)).
Persistir dados no SQLite não equivale a oferecer retomada completa da partida
pela interface após recarregar a página.

## Estrutura atual do projeto

```text
entre-linhas/
├── backend/                 # API, banco e regras Python
│   ├── app.py
│   ├── db.py
│   ├── jogo.py
│   ├── palavras.py           # Catálogo inicial de 200 palavras
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
├── scripts/ci/              # Execução de testes frontend e proteção do deploy
├── Dockerfile               # Backend e imagem integrada Railway
├── compose.yaml
├── Jenkinsfile
├── railway.json
└── README.md
```

Para executar e manter a interface web, consulte o [guia do front-end](frontend/README.md).
