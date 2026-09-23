# Testes da interface web

## Testes de interface e cliente HTTP

`tests/frontend.test.mjs` contém quatro testes unitários dos módulos JavaScript:
dois sem mock (`validarPlacar` e `validarEstado`) e dois com `fetch` simulado
(`chamarAPI` com sucesso e com erro HTTP 500). Execute com `npm run test:unit`.

`cypress/e2e/interface-partida.cy.js` contém quatro cenários de navegador: dois
sem interceptação de rede (geração de campos e bloqueio de nome vazio) e dois
com `cy.intercept()` (erro HTTP 500 e tela final após vitória simulada).
O caso de nome vazio é negativo e verifica a mensagem, o campo inválido e
a permanência na tela de nomes.

O fluxo completo sem mock, da criação da partida até a atualização do placar,
depende de uma API compatível com o contrato em `static/README.md`. A API Flask
atual em `app.py` espera `num_jogadores`, responde sem o estado completo e não
oferece `/partida/<id>/dica`; por isso esse fluxo ainda não é executável.
Os testes Cypress são de interface e não substituem os quatro testes unitários.

Os testes usam Cypress e geram um relatório Mochawesome em HTML e JSON.

## Escopo atual

A API Flask existe, mas ainda não implementa o contrato esperado pelo front-end.
A suíte abre a interface real no navegador e usa
`cy.intercept()` para responder às chamadas HTTP com dados de contrato definidos
em `fixtures/partida.json` e nos cenários. Esses dados existem somente nos testes;
nenhum modo de demonstração é adicionado a `static/`.

As verificações cobrem navegação, formulários e renderização da interface. Os novos
cenários também conferem o corpo enviado pelo navegador e o status 500 simulado.
Não comprova regras Python, cálculo de pontuação, persistência SQLite ou integração
com uma API real. Os resultados de acerto e erro são respostas controladas, não
decisões calculadas pelo teste. A aplicação atualmente envia somente a quantidade
de jogadores; preencher os nomes não significa que eles foram persistidos.

## Preparar e executar

Requisitos: Node.js 22, 24 ou 26+, npm e Python 3 acessível como `python3`.
O Python é usado somente para servir os arquivos estáticos durante esta suíte.

Na raiz do repositório:

```sh
npm ci
npm run test:unit
npm run test:e2e
```

No Windows, use `npm run test:e2e:windows` no lugar de `npm run test:e2e`.

O comando inicia o servidor em `http://127.0.0.1:8000`, espera a página responder,
executa o Cypress com Electron e encerra o servidor ao terminar, inclusive quando
um teste falha. A porta 8000 deve estar livre. O código de saída é diferente de zero
quando a suíte falha, permitindo sua execução em CI.

Para acompanhar os testes no navegador interativo:

```sh
npm run test:e2e:open
```

Se o servidor já estiver em execução, use `npm run e2e:run` ou `npm run e2e:open`.
Para testar em outra origem já servida:

```sh
npm run e2e:run -- --config baseUrl=http://127.0.0.1:8080
```

Em ambientes onde os scripts de instalação forem bloqueados, instale o navegador
de testes explicitamente com `npx cypress install`. Em Linux, o navegador também
precisa das [dependências de sistema do Cypress](https://docs.cypress.io/app/get-started/install-cypress).

## Cenários

- Fluxo completo em desktop (1280×900) e celular (390×844): iniciar, preencher nomes,
  revelar/ocultar carta, dar dica, selecionar/trocar palpite, receber acerto, passar
  ao próximo jogador, receber erro, visualizar resultado e voltar ao início.
- Quantidade de jogadores fora do intervalo 2–6.
- Nomes vazios ou compostos apenas por espaços; preservação dos nomes ao voltar
  e alteração para seis jogadores.
- Dica vazia ou com mais de uma palavra; desmarcação de coordenada e bloqueio de
  confirmação sem seleção.

Os testes aguardam as respostas simuladas por aliases apenas para sincronizar as
mudanças de tela, sem esperas fixas. Cada teste começa com uma nova visita à página
e seus próprios dados. A suíte original tem cinco casos: dois fluxos completos
(desktop e celular) e três cenários de validação e interação dos formulários.
Os quatro casos adicionais estão descritos acima.

## Relatório Mochawesome

Após `npm run test:e2e`, abra `reports/cypress/index.html` no navegador. O relatório
contém casos executados, aprovações/falhas, duração e capturas dos resultados em
desktop e celular. Falhas também geram screenshots automaticamente.

- `reports/cypress/index.html`: relatório compartilhável, com estilos e imagens
  incorporados no arquivo.
- `reports/cypress/index.json`: resultado estruturado da execução.
- `reports/cypress/screenshots/`: capturas do navegador.

Os artefatos são ignorados pelo Git e substituídos na próxima execução. Para guardar
o resultado de uma entrega, copie o relatório ou arquive `reports/cypress/` no CI.
Não é necessário abrir o Cypress Cloud nem configurar uma conta.

Versione `package.json`, `package-lock.json`, `.nvmrc`, `cypress.config.js` e os
arquivos de `cypress/e2e/`, `cypress/fixtures/` e `cypress/support/`. Dependências
instaladas, caches, downloads e relatórios gerados ficam fora do Git.

A integração segue a [configuração do cypress-mochawesome-reporter](https://github.com/LironEr/cypress-mochawesome-reporter).

Trocar apenas `baseUrl` nesta suíte não remove as respostas simuladas nem passa a
validar o backend. Testes de API e banco ficam fora deste escopo.
