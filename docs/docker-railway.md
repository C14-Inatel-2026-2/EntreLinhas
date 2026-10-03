# Docker, testes e Railway

## Armazenamento

| Componente | Montagem | Finalidade |
| --- | --- | --- |
| Aplicação local | Volume nomeado `jogo-data` em `/data` | Persistir SQLite entre reinícios e deploys |
| Aplicação Railway | Volume Railway em `/data` | Persistir `/data/jogo.db` |
| Testes Python | `./reports/backend` em `/app/reports/backend` | JUnit, cobertura XML e HTML no workspace |
| Testes JavaScript | `./reports/frontend` em `/app/reports/frontend` | Resultado dos testes e cobertura LCOV |
| Testes Cypress | `./reports/cypress` em `/app/reports/cypress` | Relatório HTML e screenshots |
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

```bash
docker compose -f compose.tests.yaml build
docker compose -f compose.tests.yaml run --rm backend-tests
docker compose -f compose.tests.yaml run --rm frontend-tests
docker compose -f compose.tests.yaml run --rm e2e-tests
docker compose -f compose.tests.yaml down
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

Referências: [volumes Railway](https://docs.railway.com/volumes),
[configuração versionada](https://docs.railway.com/config-as-code/reference) e
[healthchecks](https://docs.railway.com/deployments/healthchecks).
