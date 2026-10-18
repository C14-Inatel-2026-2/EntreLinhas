# CI/CD automático no Jenkins

O job `EntreLinhas-Deploy` usa Poll SCM a cada dois minutos (`H/2 * * * *`).
Não há GitHub Actions nem necessidade de expor o Jenkins local à internet.

## Uso do grupo

1. Crie uma branch, faça commits descritivos e envie-a ao GitHub.
2. Abra uma PR para `main` e peça a revisão de outro integrante.
3. Depois da aprovação, faça o merge. Aprovação e merge não são automáticos.
4. O Jenkins detecta a nova revisão da `main`, fixa seu SHA e executa o pipeline.
5. Se todos os stages passarem, publica no Railway e verifica versão, banco e interface.

| Stage | Responsável / entrega |
| --- | --- |
| Preparar commit e Build | Preparação compartilhada da integração |
| Testes de jogo e baralho - Caio | PR #42 |
| Backend e cobertura - Henrique | PR #44 |
| Frontend/Cypress - Mateus | PR #45 |
| Deploy - Fernando | PRs #25 e #46 e integração |

Os testes de jogo e baralho executam uma vez no stage do Caio. O stage do Henrique
exclui esses dois arquivos e usa `--cov-append` para agregar a cobertura das duas
execuções. Cada stage publica seu JUnit e seus artefatos HTML/XML.

## Política de publicação

A publicação automática só é habilitada quando a causa da execução é
`hudson.triggers.SCMTrigger$SCMTriggerCause`. Nesse caso, parâmetros manuais
anteriores são ignorados e o checkout usa a `main`. O job mantém apenas uma
execução por vez. Se a `main` mudar durante uma execução, a próxima consulta
pode agendar outro build; cada build preserva seu SHA do início ao fim.

Build manual continua disponível: `COMMIT_SHA` seleciona a revisão e `DEPLOY`
desmarcado valida sem publicar. O deploy exige aprovação de domínio, backend e
frontend para o mesmo SHA, além de checkout limpo e a credencial existente
`railway-project-token`. O autodeploy do Railway deve permanecer desativado.

## Jenkins local

O computador, Docker e Jenkins precisam ficar ligados e conectados à internet.
Se estiverem desligados, a consulta e as publicações ficam suspensas até voltarem.
Vários commits entre duas consultas podem ser reunidos em um build da ponta da
`main`; o Jenkins não promete um deployment separado para cada commit intermediário.

A configuração atual usa **Pipeline script**. O gatilho fica versionado no
`Jenkinsfile`; ao alterar o próprio pipeline, atualize também o script salvo no
job. Alterações no código da aplicação são baixadas automaticamente em cada build.

## Validação da ativação

Em 17/10/2026, o build #2 do job `EntreLinhas-Deploy` terminou em **SUCCESS**,
executando o commit `ef63478622ac2232ce0e913eb35010dee0d1edba`, sem publicar:

- 21 testes de domínio no stage do Caio e 23 de backend no stage do Henrique;
- cobertura agregada de 90,46%, com JUnit, XML e HTML arquivados;
- 4 testes unitários JavaScript e 19 cenários Cypress aprovados;
- 9 testes de bloqueio de deploy e limpeza aprovados, sem casos ignorados.

As expressões de decisão do próprio Jenkinsfile também foram executadas no
Jenkins com três causas/combinações controladas, todas com resultado SUCCESS:
manual sem deploy, manual com deploy e `SCMTriggerCause` com `DEPLOY=false` e
`COMMIT_SHA` antigo. O caso automático habilitou a publicação e ignorou o SHA
manual; esse diagnóstico não fez upload nem publicou no Railway.

O polling real consultou `refs/heads/main` e registrou `No changes`, sem criar
build desnecessário. A primeira publicação automática de uma alteração real
ocorrerá após uma próxima mudança na `main`, incluindo o merge desta PR por
um integrante. Os artefatos locais estão em `reports/ci-automacao/`, ignorado
pelo Git. Nenhuma PR foi aprovada ou integrada pela automação.
