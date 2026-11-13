# Entre Linhas — Versão Web

Jogo de cartas cooperativo de dedução para navegador, baseado no jogo físico *Entre Linhas*
(PaperGames). Projeto desenvolvido para a disciplina C14 - Engenharia de Software (Inatel).

**[Jogar Entre Linhas online](https://entrelinhas-production-7e6e.up.railway.app/static/index.html)**

## Navegação

- [Como funciona o jogo](#como-funciona-o-jogo)
- [Instalação](#instalação) e [execução](#execução)
- [Arquitetura e API](#arquitetura-e-api)
- [Organização da interface](#organização-da-interface)
- [Docker](#docker) e [Jenkins/Railway](#deploy-jenkins--railway)
- [Funcionalidades](#funcionalidades) e [testes](#testes)
- [Requisitos funcionais e não funcionais](#requisitos-funcionais-e-não-funcionais)
- [Histórias de usuário](#histórias-de-usuário)
- [Metodologia de desenvolvimento](#metodologia-de-desenvolvimento)
- [Dinâmica de desenvolvimento e refatorações](#dinâmica-de-desenvolvimento-e-refatorações)
- [Evidências da entrega](#evidências-da-entrega)
- [Refactorings](#refactorings)
- [Uso de IA](#uso-de-ia)

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

## Tempo de partida e desempenho

O relógio conta o **tempo total decorrido**, sem limite de duração da partida. Após
o envio da dica, o time tem **2 minutos para adivinhar**. Ao esgotar esse prazo,
a carta é descartada, soma um erro e o jogo avança para a próxima rodada. A fase
de dica não tem limite. Continua durante os diálogos e as trocas de turno; para
no encerramento e o resultado usa a data de término persistida no SQLite.

No final, a API retorna `duracao_segundos` e `desempenho`. A avaliação do tabuleiro
web 3 × 3 segue as faixas oficiais do modo **Expresso**:

| Acertos (de 9) | Classificação |
| --- | --- |
| 0–3 | Fracasso |
| 4–5 | Mediano |
| 6–7 | Bom |
| 8–9 | Espetacular |

A duração é mostrada apenas como informação, sem limite, comparação com tempo
alvo ou efeito na classificação. No encerramento antecipado, o resultado é
identificado como **parcial**, com as cartas não jogadas.

Fonte: [página oficial da PaperGames](https://papergames.com.br/entre-linhas/) e
[manual brasileiro, Regras v1.0, páginas 3 e 6](https://comparajogos-forum.s3.dualstack.sa-east-1.amazonaws.com/uploads/original/2X/6/6005a7acc0eed14f06f6d5406857c4c6123b1651.pdf).
O [atalho oficial do manual](https://ppgam.es/entre-linhas-regras) direciona ao
OneDrive; o PDF acima é uma cópia pública do manual da editora. **Adaptação web:**
o tempo total é livre; o limite de 2 minutos por palpite é uma regra da versão
web, sem relação com a pontuação oficial por acertos. Apenas a tabela por acertos
é usada na avaliação. O fluxo web
permanece em turnos, diferente do jogo físico simultâneo.

`POST /partida/<id>/tempo` verifica o prazo e aplica o descarte quando necessário.
O frontend envia `turno` e `fase` para que pedidos antigos não penalizem a rodada
seguinte; em falha HTTP, há nova tentativa automática. O início da fase de palpite
fica em `turno_inicio` no SQLite. Bancos existentes são migrados sem apagar
partidas; palpites antigos sem início registrado recebem dois minutos na migração.


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
| `backend/app.py` | Rotas HTTP, validação das entradas e coordenação entre regras e banco |
| `backend/jogo.py` | Regras usadas pela API (dica, avanço da rodada, tempo, placar e desempenho) e montagem do estado |
| `backend/db.py` | Inicialização, consultas e persistência SQLite |
| `backend/palavras.py` | Catálogo inicial de palavras |
| `backend/src/` | Classes de domínio em memória (`Baralho`, `Tabuleiro`, `Jogo`) e execução de terminal; a API usa apenas `Baralho` |

As regras usadas pela API têm uma única implementação, em `backend/jogo.py`,
como funções sem estado: cada requisição lê a partida do SQLite, aplica a regra
e grava o resultado. A classe `Jogo` de `backend/src/jogo.py` guarda a partida
em memória e, por isso, não é usada pela API; permanece como modelo de domínio,
coberta por `backend/tests/test_jogo.py` no stage de testes de jogo e baralho
([issue #8](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/8)).

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

## Organização da interface

A interface é uma SPA em HTML, CSS e JavaScript nativos, sem framework, bundler
ou etapa de compilação. `frontend/static/index.html` reúne as telas
**início → nomes → jogo → resultado** e carrega `js/app.js` como módulo.
Abra a aplicação por HTTP; os módulos não devem ser executados via `file://`.

| Arquivo ou diretório | Responsabilidade |
| --- | --- |
| `frontend/static/js/app.js` | Navegação, estado visual e coordenação das ações |
| `frontend/static/js/config.js` | Endereço da API; `API_BASE = ""` usa a mesma origem |
| `frontend/static/js/services/api.js` | Fetch, JSON, timeout e tratamento de erros |
| `frontend/static/js/ui/jogadores.js` | Campos de nomes e validação do formulário |
| `frontend/static/js/ui/tabuleiro.js` | Renderização, seleção e foco das células |
| `frontend/static/js/ui/dialogos.js` | Ciclo de vida e foco dos diálogos |
| `frontend/static/js/utils/turno.js` | Cálculo dos participantes e papéis do turno |
| `frontend/static/js/utils/dom.js` | Acesso aos elementos da página |
| `frontend/static/js/utils/validacao.js` | Validação do formato das respostas da API |

Os nomes permanecem na memória da interface; a API recebe a quantidade de
jogadores. A ordem de quem dá a dica é sorteada; em dupla, a outra pessoa
confirma o palpite, e em grupos maiores o time adivinha sem o autor da dica.
O contrato de estados e rotas está em [Arquitetura e API](#arquitetura-e-api).

O HTML carrega `css/style.css`, que importa os estilos na ordem **base → layout
→ componentes → telas**. `base/` reúne tema e acessibilidade; `layout/`, a
estrutura; `components/`, os elementos reutilizáveis; `pages/`, os estilos de
cada tela. Media queries e animações ficam próximas ao componente correspondente;
a preferência global por movimento reduzido fica em `base/global.css`.
Novos arquivos CSS devem ser importados em `style.css`, sem duplicar estilos.

## Docker

Para volumes, testes em containers e deploy no Railway, consulte
[Docker e Railway](#docker).

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

### Armazenamento e decisões de infraestrutura

| Componente | Armazenamento |
| --- | --- |
| Jogo local | Volume `jogo-data`, em `/data` |
| Railway | Volume do serviço em `/data`, com SQLite em `/data/jogo.db` |
| Jenkins | Volume externo `jenkins-entrelinhas-home`, em `/var/jenkins_home` |
| Testes | Banco temporário e relatórios exportados para o workspace |

O backend semeia 200 palavras sem duplicar registros nas reinicializações.
Cada partida guarda as seis palavras sorteadas em `estados_partida.palavras`.
As migrações preservam as partidas existentes; não é preciso apagar o banco.
Não monte volumes sobre o código da imagem nem use `down -v` para uma aplicação
cujos dados deseja preservar.

O Compose usa redes separadas para aplicação e testes. Frontend e backend
executam sem privilégios, com sistema de arquivos somente leitura, capacidades
removidas e diretórios temporários graváveis. Logs têm rotação. O Nginx atende
na porta interna 8080 e encaminha as rotas da API ao Gunicorn.
As imagens base são fixadas por digest; atualizar exige trocar o digest e
validar os testes. `.dockerignore` exclui bancos e segredos do contexto.

Os builds usam a raiz do repositório. O Dockerfile Python separa dependências,
testes e runtime; os Dockerfiles de frontend copiam apenas sua área. No Railway,
a imagem integra frontend e backend em um serviço; a separação de containers
é específica do Compose local. O entrypoint ajusta a propriedade do volume e
reduz privilégios antes de iniciar o Gunicorn. Backups do volume Railway devem
ser configurados no serviço.

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

A entrega utiliza **stages por integrante**, conforme o critério esclarecido
pelo grupo. Eles são coordenados por um único job Jenkins: `Preparar commit` → `Build` →
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

### Histórico de validação da CI

Em 17/10/2026, a integração foi validada no SHA
`886183cbb4e62471d95abd509975b7899d81728b`, com Groovy Sandbox e `DEPLOY=false`:
44 testes Python, 4 unitários JavaScript, 19 Cypress e 8 de proteção/limpeza
aprovados. O build terminou em SUCCESS e não publicou em produção. Esse é um
registro histórico, anterior às contagens atuais.

O build #2 do job `EntreLinhas-Deploy`, também de 17/10, validou
`ef63478622ac2232ce0e913eb35010dee0d1edba`, sem publicação: 21 testes de domínio,
23 de backend, 4 JavaScript, 19 Cypress e 9 de proteção/limpeza; cobertura Python
agregada de 90,46%. O build #3 validou a publicação automática por SCM no SHA
`7b9ca36fafa6e0508d8e620ecf2bf0de44358df9`. O build final #20, de 11/11, está
identificado em [Evidências da entrega](#evidências-da-entrega).

A integração corrigiu a seleção de specs para incluir API real e a limpeza de
processos/bancos em falhas. Uma VM com cerca de 2 GB apresentou encerramentos
por memória ao executar controladores simultâneos; a execução limpa passou.
A recomendação operacional é reservar pelo menos 4 GB ao Docker e manter um
único controlador Jenkins para a mesma automação.

Os relatórios históricos foram exportados para `reports/ci-validacao/` e
`reports/ci-automacao/`, ignorados pelo Git. Novas máquinas precisam executar o
pipeline para gerar seus próprios artefatos. O job usa Pipeline script: mudanças
no Jenkinsfile exigem atualizar também o script salvo no job. Com o computador
ou Jenkins desligados, polling e deploy ficam suspensos; várias alterações
entre consultas podem ser reunidas em um build do SHA mais recente.

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

## Requisitos funcionais e não funcionais

### Regras, turnos e dicas

| ID | Requisito | Evidência |
| --- | --- | --- |
| RF-REG-01 | A partida aceita de 2 a 6 jogadores; outros valores são recusados com 400 | `test_inicio_rejeita_quantidade_invalida` |
| RF-REG-02 | A grade 3 × 3 usa seis palavras distintas do catálogo, fixas durante a partida | `test_palavras_sorteadas_permanecem_durante_toda_partida` |
| RF-REG-03 | As nove cartas (A1 a C3) são embaralhadas e cada uma é jogada uma única vez | `test_ordem_sorteada_repete_ciclo_e_coordenadas_nao_repetem` |
| RF-REG-04 | A partida termina após a nona rodada ou por encerramento antecipado, registrando a pontuação final | `test_partida_termina_apos_todas_as_cartas`, `test_encerramento_antecipado_persiste_e_bloqueia_novas_jogadas` |
| RF-TUR-01 | A ordem de quem dá a dica é sorteada no início e se repete em ciclo | `test_ordem_sorteada_repete_ciclo_e_coordenadas_nao_repetem` |
| RF-TUR-02 | Cada rodada segue as fases dica → palpite; ações fora da fase são recusadas com 409 | `test_api_rejeita_dica_invalida_e_palpite_fora_de_fase` |
| RF-TUR-03 | A interface indica quem dá a dica e quem adivinha; com três ou mais jogadores, quem deu a dica não participa do palpite | Cypress `interface-partida.cy.js` |
| RF-DIC-01 | Na fase de dica, a API envia a carta secreta ao jogador da vez; na fase de palpite, não a envia | `test_dica_palpite_e_placar_sao_persistidos` |
| RF-DIC-02 | A dica deve ter uma única palavra, sem espaços, não vazia e com até 60 caracteres; caso contrário, é recusada com 400 | `test_dica_invalida_e_recusada_sem_mudar_a_fase`, `test_api_rejeita_dica_invalida_e_palpite_fora_de_fase`; Cypress `partida.cy.js` |
| RF-DIC-03 | Uma dica válida muda a partida para a fase de palpite e é exibida aos demais | `test_dica_palpite_e_placar_sao_persistidos` |
| RF-DIC-04 | A dica é gravada com a jogada (jogador, coordenada correta e tentada) | `test_dica_e_gravada_junto_com_a_jogada` |

Limitações: não há autenticação, então a identificação do jogador da vez ocorre
apenas na interface. A regra de palavra única considera separadores em branco, de modo
que palavras com hífen são aceitas.

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
não a integração com Python/SQLite. Consulte o [guia dos testes](#testes-de-interface-e-api-real)
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
POSIX. Veja os [resultados históricos de integração](#histórico-de-validação-da-ci)
e a [configuração de CI automático](#deploy-jenkins--railway).

Para gerar cobertura e relatórios Python, a partir de `backend/`:

```bash
python -m pytest tests --cov=app --cov=db --cov=jogo --cov=palavras --cov=src --cov-report=term-missing --cov-report=html:../reports/backend/htmlcov --junitxml=../reports/backend/junit.xml
```

Abra `reports/backend/htmlcov/index.html` para a cobertura. O JUnit é consumido
pelo Jenkins; os artefatos de cada execução ficam arquivados no build. Contagens
de testes e percentuais registrados em documentos históricos correspondem ao
commit daquela execução e devem ser regenerados para a entrega final.

### Testes de interface e API real

`frontend/tests/frontend.test.mjs` verifica os validadores de resposta e o
cliente HTTP, incluindo sucesso e erro com `fetch` simulado. Os testes de
`tabuleiro.test.mjs` usam DOM simulado; `turno.test.mjs` verifica os papéis dos
participantes. Eles complementam os cenários executados no navegador.

`frontend/cypress/e2e/` usa `cy.intercept()` e dados de contrato em
`frontend/cypress/fixtures/partida.json`. Não existe modo de demonstração na
aplicação. Essa suíte verifica navegação, nomes, dicas, seleção, diálogos,
foco, teclado, cronômetro, encerramento e falhas HTTP em desktop e celular.
Trocar apenas `baseUrl` mantém as interceptações desses cenários.
`frontend/cypress/real-api/fluxo.cy.js` verifica criação, dica, palpite, nove
rodadas e encerramento com Flask e SQLite reais.

Para reproduzir o stage completo em Linux ou macOS, com dependências instaladas,
execute na raiz usando o Python do ambiente virtual:

```bash
python scripts/ci/frontend.py
```

O executor roda os unitários, inicia Gunicorn em uma porta temporária com banco
SQLite descartável, executa todos os Cypress e encerra os processos ao terminar.
O Jenkins define `CYPRESS_BROWSER=chromium`; localmente o padrão é Electron.

Com Flask já iniciado em `127.0.0.1:5000`, é possível rodar apenas a API real,
a partir de `frontend/`:

```bash
npx cypress run --browser electron --spec cypress/real-api/fluxo.cy.js --config specPattern=cypress/real-api/fluxo.cy.js,baseUrl=http://127.0.0.1:5000
```

Essa execução manual cria partidas no banco configurado do Flask; prefira um
banco descartável. Para depuração interativa, use `npm run test:e2e:open` com
servidor estático, ou `npm run e2e:open` com um servidor já iniciado. A suíte
estática usa a porta 8000 e a libera ao terminar, inclusive em falha.

Os relatórios ficam em `frontend/reports/cypress/index.html` e `index.json`,
com capturas em `screenshots/`; os unitários geram resultado e LCOV em
`frontend/reports/frontend/`. Os artefatos são ignorados pelo Git e podem ser
substituídos na próxima execução; para a entrega, use os arquivados no Jenkins.
Não é necessário usar Cypress Cloud. Se a instalação do navegador tiver sido
bloqueada, execute `npx cypress install` em `frontend/`.

### Testes em containers

Os serviços de teste ficam no perfil `tests` do Compose. O nome de projeto
separado evita interferir na aplicação local. Execute os comandos na raiz:

```bash
docker compose -p entrelinhas-tests --profile tests build backend-tests frontend-tests app-test e2e-tests
docker compose -p entrelinhas-tests --profile tests run --rm backend-tests
docker compose -p entrelinhas-tests --profile tests run --rm frontend-tests
docker compose -p entrelinhas-tests --profile tests run --rm e2e-tests
docker compose -p entrelinhas-tests --profile tests down
```

Execute cada comando conferindo seu código de saída e faça a limpeza mesmo se
um teste falhar. A API dos testes usa armazenamento temporário e não acessa o
volume do jogo. Os relatórios são exportados para `reports/` na raiz, incluindo
`reports/cypress/index.html`. Para execuções concorrentes, use nomes de projeto
e workspaces distintos.

## Histórias de usuário

As histórias são registradas pelos próprios autores e vinculadas ao
[Projects do grupo](https://github.com/orgs/C14-Inatel-2026-2/projects/3).
Situação conferida em **11/11/2026**: as cinco histórias estão entregues e suas issues estão encerradas. Os cenários correspondentes foram validados na versão descrita em [Evidências da entrega](#evidências-da-entrega).

| História | Autor | Issue | Situação na conferência |
| --- | --- | --- | --- |
| US01 — Enviar uma dica | Caio | [#59](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/59) | Entregue |
| US02 — Registrar um palpite | Henrique | [#57](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/57) | Entregue |
| US03 — Iniciar uma partida | Mateus | [#63](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/63) | Entregue |
| US04 — Acompanhar o resultado | Fernando | [#60](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/60) | Entregue |
| US05 — Encerrar uma partida antecipadamente | Fernando | [#61](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/61) | Entregue |

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

### US01 — Enviar uma dica (Caio Rodrigues)

Como jogador da vez, quero enviar uma dica de uma única palavra sobre a minha
carta secreta, para que os outros jogadores consigam adivinhar a coordenada
correta no tabuleiro.

- **Issue:** [US01 — #59](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/59)
- **Prioridade:** Alta
- **Status:** Entregue; issue encerrada e cenários validados em 11/11/2026.
- **Evidências:** [PR #20](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/20)
  e [PR #56](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/56); testes em
  `backend/tests/test_api_jogo.py` e `frontend/cypress/e2e/`
- **Requisitos:** [regras, turnos e dicas](#regras-turnos-e-dicas)

### US02 — Registrar um palpite (Henrique Rodrigues)

Como jogador, quero registrar meu palpite para descobrir se acertei e acompanhar minha pontuação.

- **Issue vinculada:** [#57](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/57)
- **Status:** Entregue; issue encerrada. Documentação incorporada pela PR #58.
- **Evidências:** PRs [#3](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/3), [#18](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/18) e [#44](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/44)

#### Requisitos Funcionais (API e Placar)
- **RF-API-01 (Registro e Validação):** A API Flask disponibiliza o endpoint `POST /partida/<id>/palpite` para receber, validar a opção selecionada e registrar a jogada.
- **RF-API-02 (Feedback e Pontuação):** O retorno da requisição informa se o palpite foi correto ou incorreto e atualiza o placar e os turnos da partida de acordo com as regras do jogo.

#### Requisitos Não-Funcionais (Persistência)
- **RNF-PER-01 (Persistência em SQLite):** As jogadas, dados da partida e o histórico do placar são persistidos de forma síncrona no banco de dados SQLite (`jogo.db`).
- **RNF-PER-02 (Tratamento de erros):** A API rejeita entradas inválidas com HTTP 400 e operações incompatíveis com a fase com HTTP 409. Não há autenticação que valide a identidade do jogador; atomicidade e recuperação completa continuam pendentes na #9.

### US03 — Iniciar uma partida (Mateus Mendonça)

Como jogador, quero iniciar uma partida com meus amigos informando o número de jogadores e os nomes para configurar o tabuleiro e distribuir as cartas iniciais.

- **Issue vinculada:** [#63](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/63)
- **Prioridade:** Alta.
- **Status:** Entregue; issue encerrada e cenários validados em 11/11/2026.

#### Requisitos funcionais

| Requisito | Comportamento verificável |
| --- | --- |
| RF-INI-01 | Configurar de 2 a 6 jogadores e exigir o preenchimento dos nomes na interface inicial |
| RF-INI-02 | Validar o envio em `POST /partida`, gerando o tabuleiro de 3x3 e distribuindo as cartas iniciais |

#### Critérios de aceite

- A interface inicial permite configurar e aceitar de 2 a 6 jogadores.
- É obrigatório preencher os nomes dos participantes para avançar; caso contrário, a interface bloqueia e exibe um erro.
- Ao enviar a requisição de início (`POST /partida`), a API valida o número de jogadores, inicializa o estado e retorna a estrutura inicial correta.
- O tabuleiro com os tópicos nas bordas é gerado e exibido corretamente assim que a partida é iniciada.
- As cartas iniciais são distribuídas automaticamente e o primeiro turno é sorteado.

#### Evidências e limitações

O tabuleiro web 3 × 3 é montado em `backend/jogo.py`. A rota `POST /partida` em `backend/app.py` cria e valida a partida; os testes em `backend/tests/test_api_jogo.py` verificam o estado inicial, os limites de jogadores e a ordem sorteada. Os cenários Cypress em `frontend/cypress/e2e/partida.cy.js` e `frontend/cypress/e2e/interface-partida.cy.js` verificam a interface e os nomes.
O baralho é embaralhado no início, e a carta secreta é apresentada ao jogador da vez em cada rodada. O estado da partida fica no SQLite; os nomes permanecem apenas na sessão da interface. Não há retomada completa após recarregar a página (#9).

### US04 — Acompanhar o resultado (Fernando)

Como jogador, quero acompanhar os participantes, os acertos, os erros e o resultado
final para saber o desempenho cooperativo da partida.

- **Issue vinculada:** [#60](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/60)
- **Prioridade:** Alta.
- **Status:** Entregue; issue encerrada e cenários validados em 11/11/2026.

#### Requisitos funcionais

| Requisito | Comportamento verificável |
| --- | --- |
| RF-RES-01 | Exibir nomes e participação no turno; atualizar acertos e erros após cada palpite válido |
| RF-RES-02 | Consultar os totais em `GET /partida/<id>/placar` e mostrar o resultado ao finalizar |

#### Critérios de aceite

- Identificar os participantes pelos nomes informados e destacar sua participação no turno.
- Iniciar o placar com zero acertos e erros; somar um acerto ou um erro após cada palpite válido.
- Retornar os totais registrados ao consultar o placar pela API.
- Exibir os totais finais após as nove cartas ou o encerramento antecipado.

#### Evidências e limitações

As PRs [#41](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/41) e
[#56](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/56) registram interface,
feedback, nomes e turnos. Em `backend/tests/test_api_jogo.py`, os testes
`test_dica_palpite_e_placar_sao_persistidos`,
`test_palpite_incorreto_descarta_carta_e_soma_erro` e
`test_partida_termina_apos_todas_as_cartas` verificam pontuação e término.
Os cenários de `frontend/cypress/e2e/interface-partida.cy.js` e
`frontend/cypress/real-api/fluxo.cy.js` cobrem placar e resultado na interface.

Validação em 30/10/2026, base `ad18e58`: 21 testes de API aprovados com
`.venv/bin/python -m pytest backend/tests/test_api_jogo.py -q`.
Os cenários Cypress foram inspecionados, sem nova execução nesta atualização.
O placar é coletivo, sem ranking individual; os nomes ficam na sessão da interface.
Não há retomada completa após recarregar a página (#9).

### US05 — Encerrar uma partida antecipadamente (Fernando)

Como jogador, quero encerrar uma partida antecipadamente para finalizar o jogo e
consultar o placar acumulado até aquele momento.

- **Issue vinculada:** [#61](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/61)
- **Prioridade:** Alta.
- **Status:** Entregue; issue encerrada e cenários validados em 11/11/2026.

#### Requisitos funcionais

| Requisito | Comportamento verificável |
| --- | --- |
| RF-ENC-01 | Permitir encerramento nas fases de dica e palpite, preservando tabuleiro e placar |
| RF-ENC-02 | Registrar término e pontuação; bloquear novas dicas e palpites com HTTP 409 |
| RF-ENC-03 | Em erro HTTP de encerramento, informar a falha e permitir nova tentativa na interface |

#### Critérios de aceite

- Permitir encerrar nas fases de dica e palpite, inclusive antes da primeira jogada.
- Retornar fase final com HTTP 200, conservando tabuleiro e placar e ocultando carta e dica.
- Persistir data de término e pontuação final; rejeitar novas dicas e palpites com HTTP 409.
- Manter resultado e data ao repetir o encerramento; retornar HTTP 404 para partida inexistente.
- Mostrar o resultado após sucesso; em falha HTTP, manter a tela da partida e permitir tentar novamente.

#### Evidências e limitações

A PR [#41](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/41) registra o
encerramento na API e na interface. Em `backend/tests/test_api_jogo.py`, os testes
`test_encerramento_antecipado_persiste_e_bloqueia_novas_jogadas` e
`test_encerrar_sem_jogadas_e_rejeitar_partida_inexistente` verificam as duas fases,
persistência, repetição e erros. Os cenários de
`frontend/cypress/e2e/partida.cy.js` cobrem encerramento e falha HTTP seguida de
nova tentativa; `frontend/cypress/real-api/fluxo.cy.js` verifica o placar persistido.

Validação em 30/10/2026, base `ad18e58`: 21 testes de API aprovados com
`.venv/bin/python -m pytest backend/tests/test_api_jogo.py -q`.
Os cenários Cypress foram inspecionados, sem nova execução nesta atualização.
O cenário de falha HTTP da interface usa resposta simulada. Falha de resposta
não comprova rollback no servidor; atomicidade e recuperação permanecem na #9.

### Requisitos de execução e CI/CD (Fernando)

| Requisito não funcional | Configuração e limite |
| --- | --- |
| RNF-EXE-01 | Executar localmente com Python e dependências de `backend/requirements.txt`; comandos de instalação para Unix e Windows nas seções anteriores |
| RNF-EXE-02 | Servir interface e API na mesma origem pelo Flask; `http.server` é usado somente na suíte de interface com respostas simuladas |
| RNF-CI-01 | Instalar dependências npm pelo lockfile e executar testes Python/JavaScript/Cypress nos stages Jenkins dos integrantes |
| RNF-CI-02 | Bloquear publicação em falha e conferir o SHA publicado por `/static/release.json`, `/health` e interface |
| RNF-CI-03 | Arquivar relatórios e cobertura; execução automática depende de Jenkins, Docker, computador e internet disponíveis |

A documentação reúne as contribuições de Henrique (#58), Fernando (#62),
Caio (#64) e Mateus (#65). As tarefas de organização #48–#51 e as histórias
#57, #59, #60, #61 e #63 estão encerradas. A conclusão funcional das histórias
não equivale a afirmar que todas as PRs tiveram aprovação formal: o registro
das revisões é apresentado nas [evidências da entrega](#evidências-da-entrega).

## Metodologia de desenvolvimento

O grupo utiliza **Kanban no GitHub Projects** para visualizar o andamento,
distribuir responsabilidades e acompanhar as entregas. O quadro
[EntreLinhas — Entregas e pendências NP2](https://github.com/orgs/C14-Inatel-2026-2/projects/3)
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

### Acompanhamento e métricas

O acompanhamento verificável ocorreu de forma assíncrona, pelas atualizações
de issues, commits e revisões de PRs. O histórico permite observar um ciclo de
documentação em 30–31/10 e outro de correção, revisão e integração em 10–11/11.
Não há atas ou calendário versionados que comprovem uma frequência fixa de
reuniões; por isso não se atribuem ao grupo reuniões diárias ou sprints formais.
DoR e DoD acima são propostas documentadas, sem registro de adoção formal.

Métrica calculada pelas datas `closedAt` das issues da API do GitHub, antes dos
ajustes da auditoria de 11/11, com limites em UTC:

| Período | Issues encerradas | Evidências |
| --- | --- | --- |
| 25–31/10/2026 | 8 | #48, #49, #50, #51, #57, #59, #60, #61 |
| 01–11/11/2026 | 2 | #66, #8 |

A #63 foi encerrada depois desse levantamento, em 11/11. A contagem inclui
tarefas documentais e de organização; não mede produtividade individual nem
representa sprints. Fonte e limites estão nas [evidências](#evidências-da-entrega).

## Dinâmica de desenvolvimento e refatorações

O fluxo documentado em [CI automático](#deploy-jenkins--railway) orienta criar uma
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
- **Execução em CI:** os [registros de validação](#histórico-de-validação-da-ci)
  descrevem limitações de memória, seleção do navegador e limpeza de processos
  e bancos temporários após falhas.

### Bloqueios, decisões e lições extraídas do histórico

Na PR #74, o cenário de teclado falhou durante a revisão. Houve novas correções
e repetição dos testes até a aprovação no SHA `7f1e38f`. A PR #73 foi atualizada
após a integração desse trabalho, preservando a separação dos módulos do tabuleiro
e dos diálogos. A PR #76 incorporou a main após a #73 para resolver o conflito
no README. Esses eventos mostram a coordenação por dependência entre mudanças.

As lições sustentadas por esses registros são: testar o SHA final depois de
resolver conflitos; validar teclado e foco no navegador; preservar todas as
suítes ao alterar o pipeline; e registrar o SHA junto do relatório para evitar
apresentar um build antigo como evidência de uma revisão nova. Para uma próxima
entrega, antecipar essa conferência reduz correções próximas do prazo. Essas
conclusões são extraídas do histórico técnico; não substituem relatos de reuniões
que não foram registrados.

## Evidências da entrega

## Versão e alcance

Main conferida: `ddf7cdc9531c6d3f08f9a11c6ddcfb725567bfde`, merge da
[PR #76](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/76).
Os resultados abaixo correspondem ao código dessa versão. A atualização
deste README ainda precisa ser integrada à main;
não se apresenta seu conteúdo local como já publicado no GitHub.

## Stages por integrante

Conforme esclarecimento do responsável pelo grupo, o requisito da entrega é
um **stage por integrante**, coordenados por um job Jenkins. Não é necessário
criar um job separado por pessoa.

| Stage | Integrante | Evidência de contribuição |
| --- | --- | --- |
| Build e testes de jogo e baralho | Caio | PR #42; Jenkinsfile e testes de domínio |
| Backend e cobertura | Henrique | PR #44; JUnit e cobertura Python |
| Frontend/Cypress | Mateus | PR #45; unitários JavaScript e Cypress |
| Deploy | Fernando | PRs #25 e #46; validação do SHA publicado |

O Jenkinsfile exige que domínio, backend e frontend aprovem o mesmo SHA antes
de publicar. Build instala as dependências e os stages seguintes executam as
suítes e arquivam os relatórios. GitHub Actions não é usado.

## Testes locais executados

A validação foi feita em cópia isolada no SHA
`bc41644a0f8095c061eaf1e5855cbd9e1a05bfa2`. Sua árvore é idêntica à main
`ddf7cdc`: `git diff ddf7cdc bc41644 --stat` não apresenta diferenças.
Alterações de testes existentes no checkout de trabalho não participaram dessa
validação.

| Comando | Diretório | Resultado |
| --- | --- | --- |
| `python -m pytest tests/ -q` | `backend/` | 99 aprovados |
| `python -m unittest discover -s scripts/ci/tests -q` | Raiz | 9 aprovados |
| `python scripts/ci/frontend.py` | Raiz | 40 unitários JavaScript e 38 Cypress aprovados |

Total: **186 testes aprovados**. Os 38 Cypress incluem quatro cenários com
Flask e SQLite reais; os demais verificam a interface com respostas simuladas.
O executor inicia servidor e banco temporários e faz a limpeza ao terminar.

Relatórios gerados na cópia de validação:

- `frontend/reports/frontend/unit.txt`: resultado dos unitários JavaScript.
- `frontend/reports/frontend/lcov.info`: cobertura JavaScript.
- `frontend/reports/cypress/index.html`: relatório HTML Cypress.
- `frontend/reports/flask.log`: log do servidor temporário.

Esses artefatos são locais e não acompanham o clone. Para gerar relatórios
Python e JUnit, usar os comandos de cobertura do README ou executar o Jenkins.
A cobertura Python do build Jenkins foi conferida posteriormente, conforme o registro abaixo.

## Builds Jenkins registrados

| Trabalho | Evidência registrada | Limite |
| --- | --- | --- |
| Caio, PR #72 | README registra build #2 do Jenkins do Caio, SHA `15f257b`, SUCCESS | Build anterior à main final |
| Caio, PR #76 | README registra build #3, SHA `54bccbc`, SUCCESS | Anterior à integração final |
| Fernando, PR #73 | Aprovação de Caio registra build #5, SHA `0255d84`, SUCCESS, DEPLOY desmarcado | Registro na revisão da PR; execução em Jenkins local |
| Mateus, PR #74 | Comentário registra build #6 em `cd466e5`; aprovação posterior em `7f1e38f` registra unitários e Cypress verdes | O build citado não corresponde ao SHA final corrigido |
| Henrique, PR #75 | Descrição registra testes locais verdes | Sem link de build antes/depois registrado na PR consultada |

Links e registros: [PR #72](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/72),
[PR #73](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/73),
[PR #74](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/74),
[PR #75](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/75) e
[PR #76](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/76).

### Build final confirmado no Jenkins

Em **12/11/2026**, após migrar o Jenkins local para o Docker Desktop, foram
conferidos os metadados, o log e os artefatos do
[build #20 de EntreLinhas-Deploy](http://localhost:8081/job/EntreLinhas-Deploy/20/):

| Evidência | Resultado |
| --- | --- |
| Início | 11/11/2026 às 20:18:46 UTC (17:18:46 em São Paulo) |
| Acionamento | SCM change, registrado no log |
| SHA validado e publicado | `ddf7cdc9531c6d3f08f9a11c6ddcfb725567bfde` |
| Resultado | **SUCCESS** |
| Domínio — JUnit | 21 testes, zero falhas/erros/ignorados |
| Backend — JUnit | 78 testes, zero falhas/erros/ignorados |
| Proteção e limpeza da CI | 9 aprovados |
| Unitários JavaScript | 40 aprovados, zero falhas |
| Cypress | 38 aprovados em seis specs |
| Cobertura Python agregada | 356/387 linhas, **91,99%**, em `reports/backend/coverage.xml` |
| Artefatos arquivados | 46 arquivos |
| Deploy | Log confirma o SHA publicado, interface e banco disponíveis |

O log termina com `Finished: SUCCESS`. Os JUnit estão em
`reports/domain/junit.xml` e `reports/backend/junit.xml`; os resultados das
outras suítes estão em `reports/backend/ci-guards.txt`,
`frontend/reports/frontend/unit.txt` e nos relatórios Cypress arquivados.
O Jenkins exige login para acesso à API e aos relatórios. A conferência foi
realizada por leitura dos arquivos no container autorizado, sem alterar a
autenticação. Os links `localhost` só abrem na máquina que hospeda o Jenkins;
para a defesa, usar o Jenkins autenticado ou exportar seus artefatos.

A observação anterior de acesso HTTP 403 permanece explicada pela exigência
de login; ela não impediu a conferência dos arquivos do build após a migração.
O build comprova o código do SHA acima, não alterações documentais locais
feitas depois dele.

## Aplicação publicada

Endereço: [Jogar Entre Linhas](https://entrelinhas-production-7e6e.up.railway.app/static/index.html).
Na conferência de 11/11/2026, as consultas públicas retornaram:

- `/static/release.json`: commit `ddf7cdc9531c6d3f08f9a11c6ddcfb725567bfde`.
- `/health`: `{"status":"ok"}`.

Isso comprova a versão e a saúde observadas naquele momento. Não identifica
sozinho o build Jenkins que publicou a versão.

## Processo, histórias e revisões

As cinco histórias #57, #59, #60, #61 e #63 estão encerradas. A autoria foi
conferida no GitHub: Henrique (#57), Caio (#59), Mateus (#63) e Fernando
(#60/#61). A documentação foi integrada pelas PRs #58, #62, #64 e #65.

As PRs de refactoring #72, #73 e #74 têm aprovação registrada por outro membro.
#75 e #76 foram integradas sem aprovação formal no GitHub; a revisão local da
#76 e os testes estão registrados nesta conferência. Não se declara que uma
revisão posterior aconteceu antes do merge.

Métrica de issues encerradas, pela API do GitHub e campo `closedAt`, em UTC,
antes das atualizações da auditoria: 8 em 25–31/10 (#48–#51, #57, #59–#61) e
2 em 01–11/11 (#66 e #8). A #63 foi encerrada depois desse levantamento em
11/11. A contagem inclui tarefas de documentação e não mede produtividade
individual. Não há registro de cadência fixa de reuniões que permita quantificá-las.

## Refactorings

### Diálogos e participantes do turno — Fernando Stein (issue #69, PR #73)

Entrega de Fernando Stein (@Stenishh), tarefa [#69](https://github.com/C14-Inatel-2026-2/EntreLinhas/issues/69),
implementada na [PR #73](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/73).

| Smell identificado | Refactoring aplicado | Motivo e comportamento preservado |
| --- | --- | --- |
| `app.js` concentrava apresentação, eventos e foco dos diálogos junto do estado e das chamadas à API. | **Extract Module:** extrair `frontend/static/js/ui/dialogos.js`. | Concentrar o ciclo de vida dos diálogos em um módulo que recebe nome, fase e retorno de foco. Preserva os textos de início, acerto, erro e tempo esgotado, o fechamento por botão/Escape e o foco após fechar; não move o estado da partida. |
| `renderizarPartida` misturava criação de elementos com cálculo dos participantes ativos e de seus papéis. | **Extract Function:** extrair `obterParticipantesDoTurno` em `frontend/static/js/utils/turno.js`. | Permitir testar a decisão sem DOM. Preserva nomes, ordem, autor da dica, palpite da outra pessoa em dupla, palpite coletivo com 3 a 6 pessoas e ausência de participantes ativos na fase final. |

Os testes unitários em `frontend/tests/turno.test.mjs` cobrem todos os autores de
dica possíveis em equipes de 2 a 6 jogadores, nas fases dica, palpite e final.
Os cenários Cypress em `dialogos.cy.js` e `participantes-turno.cy.js` verificam
abertura, fechamento, foco e a apresentação dos papéis na interface.
Os testes de cronômetro também verificam o diálogo de tempo esgotado, incluindo
expiração na última carta, o botão “Ver resultado” e o foco no resultado final.

Evidências atuais no Jenkins local, com `DEPLOY=false` e relatórios arquivados:

- Base antes dos refactorings de Fernando, já com a PR #74 de Mateus:
  [build #2](http://localhost:8081/job/EntreLinhas-Refactoring-69/2/), commit
  `5f3a595167e18431ca36cc118cfdf1851ab89168`, **SUCCESS**:
  81 testes Python, 19 unitários JavaScript e 27 cenários Cypress.
- Integração depois dos refactorings de Fernando:
  [build #1](http://localhost:8081/job/EntreLinhas-Refactoring-69/1/), commit
  `2edc7c833608c6d810dbdb419439287e0875990c`, **SUCCESS**:
  81 testes Python, 40 unitários JavaScript, 38 cenários Cypress e 9 testes de
  proteção da CI; cobertura Python agregada de aproximadamente 92%.

O job isolado `EntreLinhas-Refactoring-69` foi recriado em 11/11/2026, com polling
removido. Por isso a numeração recomeçou em #1. Os builds #4 e #6 da instalação
anterior, registrados na PR, não estão disponíveis nesta instância; os links
acima são as evidências acessíveis atuais e exigem acesso ao Jenkins local.

O registro histórico anterior apontava **SUCCESS** para a base `3ee8280`
(build #4: 73 testes Python, 4 unitários JavaScript e 26 cenários Cypress) e para
`125471c` (build #6: 73 testes Python, 25 unitários JavaScript e 36 cenários Cypress).
Esses registros históricos não substituem os novos builds da integração.

A branch incorpora a PR #74 de Mateus (#68), integrada na `main` pelo commit
`5f3a595167e18431ca36cc118cfdf1851ab89168`. O novo cenário cobre expiração na última
carta. A validação do commit final que inclui este registro fica vinculada na PR.
A aprovação independente está registrada na PR #73. O build #20 do job
`EntreLinhas-Deploy` validou a main integrada `ddf7cdc` e publicou essa versão;
veja as [evidências da entrega](#evidências-da-entrega). Os builds
isolados citados acima não publicaram em produção.

### Regras e montagem do estado — Caio Rodrigues (issues #66 e #8, PRs #72 e #76)

Refactorings sem mudança de comportamento. Antes de cada um, testes de
caracterização fixaram o comportamento, e os mesmos testes passam depois:
`backend/tests/test_placar_tabuleiro.py` para o placar e o JSON completo de
`montar_estado` (1 e 2) e `backend/tests/test_regras_rodada.py` para a regra
da dica e o avanço da rodada (3 e 4).

| # | Smell | Refactoring aplicado | Por quê | PR | Autoria |
| --- | --- | --- | --- | --- | --- |
| 1 | Código duplicado: acertos, erros e pontuação final calculados em cinco trechos de `backend/app.py` e em `backend/jogo.py`, ora somando `acertou`, ora contando coordenadas | Extract Function: `calcular_placar` e `coordenadas_acertadas` em `backend/jogo.py`, usadas pela rota `/placar`, pelo palpite, pelo tempo esgotado, pelo encerramento e por `montar_estado` | A regra de pontuação passa a existir em um só lugar; mudar a contagem não exige lembrar de cinco rotas | [PR #72](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/72) | Caio Rodrigues |
| 2 | Função longa: `montar_estado` monta tabuleiro, placar, tempo, desempenho e resumo | Extract Function: `montar_tabuleiro(palavras, acertos)` em `backend/jogo.py` | Separa a composição da grade 3 × 3 do restante do estado e permite testá-la isoladamente, com o mesmo JSON | [PR #72](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/72) | Caio Rodrigues |
| 3 | Regra de domínio dentro da rota: `rota_dica` validava a dica em uma condição longa e repetia a mensagem de erro em dois `return` | Extract Function: `dica_valida(dica)` em `backend/jogo.py` | A regra da dica ganha nome e fica junto das outras regras; a rota só lê a entrada e responde | [PR #76](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/76) | Caio Rodrigues |
| 4 | Código duplicado: o cálculo do próximo índice e da fase (`dica` ou `final`) estava repetido em `_penalizar_tempo` e em `rota_palpite` | Extract Function: `proxima_rodada(progresso)` em `backend/jogo.py` | O fim da partida passa a ser decidido em um só lugar, tanto no palpite quanto no tempo esgotado | [PR #76](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/76) | Caio Rodrigues |

Pipeline do Jenkins antes e depois das alterações 1 e 2, com disparo manual e
`DEPLOY` desmarcado:

| Momento | SHA | Build | Resultado |
| --- | --- | --- | --- |
| Antes (base na `main`) | `3ee82801008e4b722bc8243e3c2bdbefff5ea509` | #4, no Jenkins local do Fernando | SUCCESS |
| Depois (SHA final da PR #72) | `15f257bf32baa1eb66ae9c3232ddb210072af5ec` | [#2 do job `EntreLinhas-Deploy`](http://localhost:8081/job/EntreLinhas-Deploy/2/), no Jenkins local do Caio | SUCCESS: 21 testes de jogo e baralho, 60 de backend e 26 do Cypress |

Os links apontam para o Jenkins local de quem executou e só abrem nessa máquina;
os prints dos builds foram compartilhados com a equipe. O commit de integração
na `main`, `57ebb50`, tem o mesmo conteúdo do SHA final testado.

Pipeline do Jenkins antes e depois das alterações 3 e 4, no Jenkins local do
Caio, com disparo manual e `DEPLOY` desmarcado:

| Momento | SHA | Build | Resultado |
| --- | --- | --- | --- |
| Antes (base na `main`) | `57ebb50d9e8c8bd60e50232cd2a045a41241f2c8`, de conteúdo idêntico ao do `15f257b` | [#2 do job `EntreLinhas-Deploy`](http://localhost:8081/job/EntreLinhas-Deploy/2/), executado no `15f257b` | SUCCESS: 21 testes de jogo e baralho, 60 de backend e 26 do Cypress |
| Depois (PR #76) | `54bccbca64b36de4957fc557f090c000201e60cf` | [#3 do job `EntreLinhas-Deploy`](http://localhost:8081/job/EntreLinhas-Deploy/3/) | SUCCESS: 21 testes de jogo e baralho, 78 de backend e 26 do Cypress |

O build #3 testou o último commit da PR #76 antes deste registro; o commit que
acrescenta esta tabela altera apenas o README.

### Conexões e inicialização do banco — Henrique Rodrigues Mendonça (issue #67, PR #75)

**SHA Base:** `3ee82801008e4b722bc8243e3c2bdbefff5ea509`

#### 1. Gerenciador de Contexto para Conexões SQLite (`get_db_connection`)
- **Code Smell:** *Resource Leak / Unclosed Connections* (abertura e fechamento manual de conexões com risco de vazamento ou locks pendentes em caso de exceções nas rotas).
- **Refactoring Aplicado:** *Extract Context Manager* (criação de `get_db_connection` em `backend/db.py` com gerenciamento automático do ciclo de vida, `rollback` em falhas e `close` garantido no `finally`).
- **Por quê:** Garante que toda conexão com o banco SQLite seja encerrada deterministicamente ao final de cada requisição HTTP em `backend/app.py`, evitando vazamento de recursos e contenção de conexões no SQLite.
- **Autor:** Henrique Rodrigues Mendonça
- **PR:** [#75](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/75)

#### 2. Extração das Etapas de Inicialização do Banco de Dados
- **Code Smell:** *Long Method / Mixed Responsibilities* (a função `criar_tabelas` acumulava DDL de schemas, carga de dados iniciais e aplicação de migrações em um único bloco de código).
- **Refactoring Aplicado:** *Extract Method* (divisão em `_inicializar_schemas`, `_popular_palavras_iniciais` e `_aplicar_migracoes_banco` em `backend/db.py`).
- **Por quê:** Melhora a legibilidade, isola responsabilidades de infraestrutura de dados e garante idempotência limpa na subida da API.
- **Autor:** Henrique Rodrigues Mendonça
- **PR:** [#75](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/75)

### Tabuleiro da interface — Mateus Mendonça (issue #68, PR #74)

Refactorings sem mudança de comportamento. Antes de cada um, testes de
caracterização em `frontend/tests/tabuleiro.test.mjs` e um cenário em
`frontend/cypress/e2e/interface-partida.cy.js` fixaram a estrutura da grade,
a seleção única, o foco e os atributos de acessibilidade; os mesmos testes
passam depois.

| # | Smell | Refactoring aplicado | Por quê | PR | Autoria |
| --- | --- | --- | --- | --- | --- |
| 1 | Módulo com várias responsabilidades: `frontend/static/js/app.js` reúne navegação, estado da partida e a renderização e seleção do tabuleiro | Extract Module: `frontend/static/js/ui/tabuleiro.js`, com interface explícita (`renderizarTabuleiro`, `selecionarCelula`, `atualizarSelecao`, `obterCelulaSelecionada`, `obterCelulaParaFoco`, `vincularSelecao`) | O tabuleiro deixa de depender das variáveis globais do `app.js` (recebe `podeSelecionar` por parâmetro), pode ser testado sem navegador e libera o `app.js` para a extração da PR de Fernando | [PR #74](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/74) | Mateus Mendonça |
| 2 | Função longa: `renderizarTabuleiro` monta cabeçalhos, linhas e células em uma única função | Extract Function: `criarCabecalho`, `criarLinha` e `criarCelulaDeCoordenada` em `frontend/static/js/ui/tabuleiro.js` | Cada função monta um nível da grade (cabeçalho, linha, célula), o que facilita testar a estrutura e os atributos ARIA isoladamente, com o mesmo DOM | [PR #74](https://github.com/C14-Inatel-2026-2/EntreLinhas/pull/74) | Mateus Mendonça |

Base das alterações: commit `3ee8280` da `main`. Os links do pipeline verde
antes e depois (com `DEPLOY` desmarcado) ficam registrados na PR.

## Uso de IA

O grupo utilizou **GPT-6 e GPT-6.1 no Codex**, conforme declaração registrada
neste projeto. A IA foi usada **individualmente**, por cada integrante em suas
próprias sessões, como apoio às tarefas sob sua responsabilidade. O trabalho
coletivo foi integrado pelo GitHub, por commits, pull requests e revisões.

**A grande maioria do código foi gerada com auxílio de IA.** As ideias para a
adaptação do jogo, as funcionalidades, as decisões de implementação e as
melhorias foram pensadas e definidas pelo grupo. Os integrantes usaram a IA
para transformar essas decisões em código e apoiar os ajustes ao longo do
desenvolvimento.

Além disso, o integrante Mateus Mendonça utilizou o **Gemini 3.5 Flash Lite** para suporte ao desenvolvimento e refatoração do módulo de tabuleiro e grade (`tabuleiro.py`), estabilização de testes E2E com Cypress, configuração do pipeline no Jenkins e ajustes de lógica e asserções com mocks nos testes do cronômetro (`backend/tests/test_cronometro.py`).

### Finalidades e dinâmica de uso

A ferramenta auxiliou na geração e no ajuste de código, refatorações, testes,
documentação, design da interface, investigação de erros e organização das
entregas. Também foi usada para consultar o histórico, revisar PRs, executar
comandos e testes e comparar requisitos com a implementação.

No frontend, o apoio envolveu HTML, CSS e JavaScript, integração com a API e
cenários Cypress. No backend, envolveu análise das regras, persistência SQLite
e testes Python. Na infraestrutura, auxiliou na configuração e investigação
do Docker, Jenkins e Railway. A documentação registra ainda seu uso para
conferir o PDF da NP2 e organizar issues e o GitHub Projects.

O uso individual não significa que toda alteração tenha sido escrita sem
assistência. Nesta sessão de integração, por exemplo, o agente executou testes,
atualizou o Projects e realizou o merge da PR #76 após instrução do responsável.
Essas ações são declaradas como trabalho assistido por IA.

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

### Prompts reais e tratamento das respostas

Os exemplos abaixo reproduzem pedidos reais de Fernando na sessão de revisão
e documentação, preservando a redação original. São exemplos do uso individual;
não atribuem esses mesmos prompts aos demais integrantes.

| Prompt real | Resposta e tratamento |
| --- | --- |
| “atualize a main e veja a pr do caio para poder aceitar ela” | A IA identificou a PR #76, examinou o diff e executou os testes em uma cópia isolada para preservar alterações locais. A recomendação de integração foi **aceita**: o responsável também instruiu “aprove e faca o merge”, e a PR foi integrada. Foram registrados 99 testes Python, 9 de proteção da CI, 40 unitários JavaScript e 38 Cypress aprovados. |
| “pq existe static/js/mocks se n tem nada?” | A investigação foi **ajustada após conferir o caminho**: a primeira consulta em `frontend/static/js/mocks` não encontrou a pasta; a busca seguinte localizou `static/js/mocks` na raiz, vazia, sem arquivos versionados ou referências encontradas. A resposta explicou que os mocks HTTP usados nos testes estão no Cypress. A pasta não foi removida nessa consulta. |
| “preencha essa parte, foram usadas individualemnte” | A documentação foi **ajustada com a informação fornecida pelo integrante**: uso individual da IA. Os exemplos anteriores eram resumos; foram substituídos por prompts reais desta sessão e pelo registro do tratamento das respostas. Também se distinguiu participação humana de código cuja autoria exclusivamente manual não foi comprovada. |
| "verifique se as alterações podem afetar de maneira negativa" (com o código do tabuleiro, app e testes colados) | A IA comparou os arquivos com a estrutura proposta, identificou pontos de melhoria e inconsistências de escopo em funções e componentes (como a extração do tabuleiro e grade para `tabuleiro.py`), indicando ajustes estruturais e de formatação. O usuário aplicou as melhorias para garantir a estabilidade do fluxo do jogo. |
| "desses testes, altere pra que comece a usar mock" (com o `test_cronometro.py` colado) | A IA analisou os testes unitários do cronômetro, identificou onde aplicar o `unittest.mock.patch` para isolar o relógio (`datetime` e `time.time`) e propôs o uso de asserções de chamadas (`assert_called` / `assert_not_called`). Validou a correção de regressões na lógica de contagem e nos testes da rota de placar. |

Esses exemplos registram uma recomendação aceita e respostas ajustadas; não se
inventa uma resposta descartada apenas para preencher uma categoria.

### Participação humana e partes feitas sem IA

O grupo foi responsável pela concepção da adaptação web do jogo, pela definição
das funcionalidades e pela escolha das melhorias. As decisões sobre o que
implementar e como a aplicação deveria funcionar partiram dos integrantes,
que orientaram individualmente a IA na produção e no ajuste do código.
O jogo físico *Entre Linhas*, que serviu de referência, é da PaperGames.

A contribuição humana concentrou-se nessas ideias e decisões, na divisão das
tarefas e na avaliação dos resultados em relação ao que o grupo pretendia
entregar. A IA teve participação ampla na escrita do código, dos testes e da
documentação, além de apoiar revisões e operações de integração. Por isso,
autoria de um commit não é apresentada como prova de programação manual.

Não se declara um arquivo ou módulo inteiro como escrito exclusivamente
“à mão” sem identificação específica pelo integrante responsável. O trabalho
intelectual do grupo e o uso amplo de código gerado por IA são declarados
em conjunto, conforme o relato dos integrantes.

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
│   └── requirements.txt     # Dependências Python
├── frontend/                # Interface e ferramentas JavaScript
│   ├── static/              # HTML, CSS e JavaScript
│   ├── tests/               # Testes unitários JavaScript
│   ├── cypress/             # Testes de navegador
│   ├── cypress.config.js
│   ├── package.json         # Dependências e comandos npm
│   ├── package-lock.json    # Versões transitivas fixadas
│   └── .nvmrc
├── docker/                  # Infraestrutura dos containers
├── scripts/ci/              # Execução de testes frontend e proteção do deploy
├── Dockerfile               # Backend e imagem integrada Railway
├── compose.yaml
├── Jenkinsfile
├── railway.json
└── README.md
```

Toda a documentação do projeto está concentrada neste README.
