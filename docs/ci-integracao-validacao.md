# Integração dos stages de testes e deploy

Validação realizada em 17/10/2026 na branch `fix/integracao-ci-mateus-fernando`.
O Jenkins executou o commit `886183cbb4e62471d95abd509975b7899d81728b`, com
Groovy Sandbox habilitado e `DEPLOY=false`. Resultado: **SUCCESS**.

## Fluxo entregue

`Preparar commit` → `Build` → `Testes de backend e cobertura` →
`Frontend/Cypress - Mateus` → `Deploy - Fernando`.

- Dependências Python e JavaScript são instaladas uma vez no Build.
- A suíte Python inclui jogo e baralho, sem um segundo stage duplicando os casos.
- O frontend executa unitários e as três suítes Cypress com Chromium no Jenkins.
  O comando CI amplia `specPattern`; somente `--spec` não incluía a pasta de API real.
- Flask herda um socket reservado, usa SQLite temporário e tem seu grupo de
  processos encerrado em sucesso, falha ou interrupção. O log é arquivado.
- O deploy exige aprovação das duas suítes para o mesmo SHA e checkout limpo.
  `DEPLOY` desmarcado permite validar sem token e sem publicar.
- Quando habilitada a publicação, o build gera `release.json` temporário e a
  verificação pública confere o commit, o banco e a interface. O marcador é
  removido do workspace ao terminar.

## Resultados

| Verificação | Resultado |
| --- | --- |
| Backend Python | 44 aprovados; cobertura total de 90% |
| Unitários JavaScript | 4 aprovados |
| Cypress com respostas simuladas | 15 aprovados |
| Cypress com Flask/SQLite reais | 4 aprovados |
| Proteção do deploy e limpeza após falha do Cypress | 8 aprovados |
| Pipeline completo no Jenkins | SUCCESS; publicação desabilitada |
| Compose e alterações de arquivos | `docker compose config --quiet` e `git diff --check` aprovados |

Os testes de proteção verificam bloqueio por ausência de aprovação, SHA divergente,
checkout alterado, versão pública antiga, erro do Railway e marcador preexistente.
O teste de limpeza sobe Gunicorn real, simula falha do Cypress e verifica a parada
do servidor e a remoção do banco. A publicação foi simulada nesses testes; nenhum
deployment de produção foi executado.

Uma execução com falha do navegador também confirmou que o pipeline arquiva os
relatórios e não chega ao stage de deploy. A VM Docker local tem aproximadamente
2 GB: executar vários Jenkins simultaneamente provocou encerramentos por memória.
A execução limpa passou com o Jenkins principal temporariamente parado. O Compose
limita o heap Java a 384 MB, configurável por `JENKINS_JAVA_OPTS`; recomenda-se
reservar pelo menos 4 GB para Jenkins e Cypress.

## Conferência local e ativação

Os artefatos da execução foram copiados para `reports/ci-validacao/` (ignorado pelo
Git), incluindo `jenkins-build.xml`, `jenkins-console.txt`, JUnit, cobertura,
relatório HTML do Cypress e screenshots. Em outro computador, execute o pipeline
para gerar novos artefatos; eles não acompanham o clone.

O Jenkins principal preserva a autenticação e o volume externo. O job
`EntreLinhas-Deploy` foi preparado com o pipeline integrado e `DEPLOY` desmarcado.
Enquanto esta branch não estiver na `main`, informe o SHA completo da branch no
parâmetro `COMMIT_SHA`. Depois de alterar o Jenkinsfile, atualize também o script
salvo no job, como descrito no README.

Para habilitar a publicação real, falta cadastrar no Jenkins a credencial
**Secret text** `railway-project-token`, com um Project Token do Railway. Nenhum
token foi lido ou incluído no código; o Jenkins local não tinha essa credencial.
Após cadastrá-la, marque `DEPLOY` para testar e publicar o SHA informado.
