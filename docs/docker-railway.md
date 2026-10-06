# Docker, testes e Railway

## Armazenamento

| Componente | Montagem | Finalidade |
| --- | --- | --- |
| Aplicação local | Volume nomeado `jogo-data` em `/data` | Persistir SQLite entre reinícios e deploys |
| Aplicação Railway | Volume Railway em `/data` | Persistir `/data/jogo.db` |
| Testes Python | `./reports/backend` em `/app/reports/backend` | JUnit, cobertura XML e HTML no workspace |
| Testes JavaScript | `./reports/frontend` em `/app/reports/frontend` | Resultado dos testes e cobertura LCOV |
| Testes Cypress | `./reports` em `/app/reports` | Relatório HTML e screenshots em `cypress/` |
| API dos testes | Memória temporária em `/data` | Banco isolado, descartado ao remover o container |

No Compose local, frontend (Nginx) e backend (Gunicorn) usam containers separados.
O Nginx encaminha `/partida` e `/health` ao backend pela rede Docker, mantendo
interface e API na mesma origem. O frontend é estático e não
precisa de volume: seus arquivos são atualizados junto com a imagem. Não monte
volumes sobre `/app` ou `/app/static`, pois isso esconderia o código da imagem.
Os testes não acessam o volume de produção.

## Execução local

```bash
docker compose up --build -d --wait
docker compose ps
```

Acesse `http://localhost:8080` para a interface. O backend também está disponível
em `http://localhost:5001`; nele `/` redireciona para `/static/index.html`.
`/health` verifica acesso ao banco. Para parar mantendo o banco:

```bash
docker compose down
```

O banco local `jogo.db` não é importado automaticamente para o volume.

## Testes em containers

Execute cada job separadamente para preservar seu código de saída:

Todos os serviços estão no `compose.yaml`. O perfil `tests` mantém os serviços
de teste fora da inicialização normal. Use o projeto `entrelinhas-tests` para
que a execução e a limpeza dos testes não interfiram na aplicação local.

```bash
docker compose -p entrelinhas-tests --profile tests build backend-tests frontend-tests app-test e2e-tests
docker compose -p entrelinhas-tests --profile tests run --rm backend-tests
docker compose -p entrelinhas-tests --profile tests run --rm frontend-tests
docker compose -p entrelinhas-tests --profile tests run --rm e2e-tests
docker compose -p entrelinhas-tests --profile tests down
```

O job Cypress inicia uma API exclusiva, aguarda sua saúde e roda os cenários
com respostas simuladas e os cenários de API real. A limpeza deve executar
mesmo quando um teste falhar (por exemplo, no bloco `post/always` do Jenkins).
Para jobs concorrentes, use um nome de projeto Compose exclusivo por build,
com `-p entrelinhas-build-<numero>` em todos os comandos, e workspaces separados.

No Jenkins, publique `reports/backend/junit.xml` com JUnit e os HTML
`reports/backend/htmlcov/index.html` e `reports/cypress/index.html` com HTML
Publisher. Arquive também `reports/backend/coverage.xml`,
`reports/frontend/unit.txt` e `reports/frontend/lcov.info`. A cobertura JavaScript
mede os módulos exercitados pelos testes unitários; Cypress gera relatório de
cenários e screenshots, sem instrumentação de cobertura de navegador.

## Railway

O Dockerfile principal continua incluindo frontend e backend para o deploy
Railway de um único serviço descrito abaixo. O Compose local separado não
altera essa configuração.

1. Crie/conecte um serviço para este repositório, com a raiz do projeto como
   Root Directory. `railway.json` seleciona o Dockerfile e `/health`.
2. Adicione um volume ao serviço com Mount Path `/data`. Isso precisa ser feito
   no projeto Railway; o arquivo `railway.json` não cria o volume.
3. Defina `DATABASE_PATH=/data/jogo.db` e `RAILWAY_RUN_UID=0` nas variáveis.
   Os volumes Railway são montados como root. O entrypoint ajusta a propriedade
   do diretório e dos arquivos SQLite, e executa o Gunicorn como usuário `app`.
4. Mantenha uma réplica, conforme `railway.json`, para este banco SQLite local.
5. Gere um domínio público. O Gunicorn usa `PORT` fornecido pelo Railway e o
   mesmo domínio atende interface e API; nenhuma URL adicional é necessária.
6. Configure backups do volume no Railway e verifique `/health` e uma partida
   após a primeira publicação.

Os jobs de teste e seus relatórios ficam no Jenkins, sem serviços ou volumes
de testes no Railway. Para atender à disciplina, desative o autodeploy por push
e deixe o job Deploy do Jenkins publicar somente depois dos testes aprovados.
A integração Jenkins/Railway ainda precisa ser configurada com as credenciais
do projeto. Não versione tokens no repositório.

## Decisões Docker

- `compose.yaml` reúne aplicação e testes; estes usam o perfil `tests`.
- O Dockerfile Python possui estágios `dependencies`, `backend-tests` e `runtime`.
  O último é o padrão do Railway. O estágio de testes reutiliza as dependências.
- As bases Python, Nginx e Cypress estão fixadas por digest. Ao atualizar, troque o digest
  e execute novamente os testes; `--pull` sozinho não troca uma base fixada.
- Dependências JavaScript usam `npm ci` e lockfile.
- Dependências são copiadas antes do código e usam cache BuildKit, sem guardar
  caches de download nas camadas finais.
- `.dockerignore` permite apenas entradas necessárias, excluindo banco e segredos.
- Backend e frontend executam como usuários sem privilégios. O Nginx escuta na
  porta interna 8080 para dispensar permissões de porta privilegiada.
- O Compose aplica `read_only`, `cap_drop: ALL`, `no-new-privileges` e `init` aos
  serviços da aplicação. Apenas SQLite e diretórios temporários são graváveis.
- Redes da aplicação e dos testes são separadas; portas públicas ficam limitadas
  a localhost. Logs da aplicação possuem rotação de 10 MB, com até três arquivos.
- Gunicorn e Nginx executam diretamente, permitindo receber sinais de parada.

Foi mantido um único `backend/requirements.txt`, conforme a escolha do grupo. Assim,
pytest e cobertura também são instalados na imagem da aplicação. Os fontes dos
testes e os relatórios ficam apenas no estágio de testes.

O Railway usa o Dockerfile; as opções de segurança do Compose são específicas
da execução local. A inicialização Railway como root serve para corrigir a
propriedade do volume, e o entrypoint reduz os privilégios antes do Gunicorn.

Referências: [volumes Railway](https://docs.railway.com/volumes),
[configuração versionada](https://docs.railway.com/config-as-code/reference) e
[healthchecks](https://docs.railway.com/deployments/healthchecks).

## Estrutura do monorepo

Os builds usam a raiz como contexto. O Dockerfile Python copia fontes e dependências
de backend/ e a interface de frontend/static/. Os Dockerfiles de frontend copiam
apenas frontend/. Compose e Railway continuam sendo executados na raiz.
