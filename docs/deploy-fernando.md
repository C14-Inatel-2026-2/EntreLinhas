# Entrega de Fernando: Deploy Jenkins → Railway

Esta entrega implementa o job Deploy e a execução com Gunicorn. Build,
testes de domínio, Cypress e cobertura ficam com os
responsáveis por essas etapas.

## O que foi implementado

- `requirements.txt` reúne Flask, Gunicorn, pytest e pytest-cov em um único arquivo.
- O Dockerfile inicia interface e API com Gunicorn, usando a variável `PORT`.
- `app.py` não inicia mais um servidor com `debug=True`.
- `Jenkinsfile` define o job Deploy de Fernando, recebendo `COMMIT_SHA`.
- O próprio Jenkinsfile publica via CLI e verifica interface e banco após o deploy.
- `.railwayignore` exclui banco local, ambientes, relatórios e segredos do upload.

Dockerfile, porta dinâmica, `/health` e configuração Railway já estavam na main
e são reutilizados. Não é necessário trocar os containers existentes.

## Execução da aplicação

```bash
docker compose up --build -d --wait
```

Acesse `http://localhost:8080`. Não há scripts auxiliares de inicialização.
O entrypoint em `docker/entrypoint.sh` prepara as permissões do volume SQLite
no Railway e reduz os privilégios antes de executar o Gunicorn.

## Configuração do Railway

No serviço EntreLinhas conectado ao repositório:

| Configuração | Valor |
| --- | --- |
| Dockerfile | `Dockerfile` na raiz |
| Healthcheck | `/health` (definido em `railway.json`) |
| Réplicas | 1 |
| Volume | Mount Path `/data` |
| `DATABASE_PATH` | `/data/jogo.db` |
| `RAILWAY_RUN_UID` | `0` |
| `PORT` | Usar o valor fornecido pelo Railway |

Gere o domínio em Settings → Networking → Generate Domain. Não sobrescreva o
Start Command: o entrypoint Docker prepara o volume e usa a porta dinâmica.
Desative o autodeploy se estiver habilitado, para o Jenkins controlar a publicação.

O primeiro deploy manual pode preparar o ambiente. Nas entregas seguintes,
o pipeline deve publicar somente depois de Build e Testes aprovados.

## Configuração do job Jenkins

1. Use um agente Linux com label `linux`, Git, Bash, Python 3 e Railway CLI.
   Instale a CLI no agente conforme a documentação oficial (com Node instalado,
   `npm install -g @railway/cli`) e confirme `railway --version`.
2. Instale os plugins Pipeline, Git e Credentials Binding.
3. Gere um **Project Token** no projeto Railway, associado ao ambiente de deploy.
   No Jenkins, salve como credencial **Secret text**, ID `railway-project-token`.
   Nunca coloque o token no Git ou nos parâmetros do build.
4. Crie o job Pipeline `entrelinhas-fernando-deploy`. Selecione **Pipeline script
   from SCM**, Git e o repositório EntreLinhas. Durante a revisão, use a branch
   `feat/fernando-deploy-jenkins`; após o merge, use `main`. Script Path: `Jenkinsfile`.
5. Preencha os parâmetros do job:

| Parâmetro | Valor |
| --- | --- |
| `COMMIT_SHA` | SHA completo que passou no Build e nos Testes |
| `RAILWAY_PROJECT_ID` | ID do projeto Railway (obtido na URL/configuração) |
| `RAILWAY_SERVICE` | `EntreLinhas` ou ID do serviço |
| `RAILWAY_ENVIRONMENT` | `production` ou ID do ambiente do token |
| `PUBLIC_URL` | `https://<dominio-gerado>` |

O job faz checkout do SHA informado, publica pelo Railway e verifica `/health`
e `/static/index.html`. Falhas de upload, deploy ou verificação encerram o job
com erro. O timeout total é 30 minutos.

## Integração com o restante do pipeline

O responsável pela integração deve chamar este job somente depois de todas as
etapas anteriores terminarem com sucesso, passando o mesmo `COMMIT_SHA` e os
parâmetros Railway. Este Jenkinsfile contém somente a parte de Deploy; não
executa nem atesta os testes dos outros integrantes. Restrinja o acionamento
manual do job conforme as permissões do Jenkins usado pelo grupo.

## Validação e pendências externas

O deploy real via Jenkins depende do servidor Jenkins, do token e do domínio
Railway. A criação dessas configurações não acontece ao adicionar arquivos ao Git.
Após conectar tudo, execute o pipeline e guarde o link/log do build para a entrega.

Referências: [Railway CLI](https://docs.railway.com/cli/deploying),
[volumes](https://docs.railway.com/volumes) e
[Credentials Binding](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/).
