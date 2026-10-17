# Frontend

Interface em HTML, CSS e JavaScript nativos, em `static/`. Não há etapa de build.
`package.json` e `package-lock.json` gerenciam as ferramentas de teste via npm.
A versão de Node está em `.nvmrc`.

Execute a partir de `frontend/`:

```sh
npm ci
npm run test:unit
npm run test:e2e
```

No Windows, use `npm run test:e2e:windows`. Os testes E2E iniciam um servidor
estático e simulam a API. Para jogar, inicie o [backend](../backend/README.md)
e abra `http://127.0.0.1:5000/`, ou use Docker Compose na raiz.

Os relatórios locais ficam em `frontend/reports/`; no Compose, são exportados
para `reports/` na raiz. Consulte a [organização da interface](static/README.md)
e o [guia Cypress](cypress/README.md).
