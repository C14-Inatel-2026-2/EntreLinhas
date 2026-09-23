# Front-end — Entre Linhas

SPA em HTML, CSS e JavaScript vanilla, sem framework ou etapa de build. As quatro telas continuam no mesmo HTML; a organização em módulos separa responsabilidades sem mudar o fluxo do jogo.

```text
static/
├── index.html              # Estrutura das telas e carregamento da aplicação
├── README.md               # Organização e integração
├── css/
│   ├── style.css           # Entrada única e ordem dos imports
│   ├── base/
│   │   ├── variaveis.css   # Paleta compartilhada
│   │   └── global.css      # Normalização, tipografia e acessibilidade
│   ├── layout/
│   │   └── estrutura.css  # Cabeçalho, área principal e rodapé
│   ├── components/
│   │   ├── controles.css  # Botões, inputs e labels
│   │   ├── paineis.css    # Superfície dos painéis
│   │   ├── feedback.css   # Avisos, erros e loading
│   │   ├── placar.css     # Acertos e erros
│   │   └── tabuleiro.css  # Grade e interação das células
│   └── pages/
│       ├── inicio.css
│       ├── jogadores.css
│       ├── jogo.css
│       └── resultado.css
└── js/
    ├── app.js              # Entrada, navegação, estado visual e tabuleiro
    ├── config.js           # Endereço da API
    ├── services/
    │   └── api.js          # Fetch, JSON, timeout e tratamento de erros
    ├── ui/
    │   └── jogadores.js    # Campos de nomes e validação do formulário
    └── utils/
        ├── dom.js          # Acesso a elementos da página
        └── validacao.js    # Validação do formato das respostas da API
```

## Executar localmente

Na raiz do repositório:

```sh
python3 -m http.server 8000 --directory static
```

Abra `http://localhost:8000`. Sirva os arquivos por HTTP: os módulos JavaScript nativos não devem ser abertos diretamente via `file://`.

Esse comando serve somente a interface. Iniciar e jogar uma partida depende da API Flask, ainda não implementada neste repositório. Ao servir o frontend separadamente, configure `API_BASE` para o endereço da API e permita a origem do frontend no backend.

No Flask, configure esta pasta como `static_folder` e abra `/static/index.html`. Os caminhos de CSS e JavaScript são relativos ao HTML; os endpoints da API são relativos à origem. Nenhum bundler é necessário.

## Fluxo e responsabilidades

`index.html` carrega somente `js/app.js`, que importa os módulos necessários. O fluxo é **início → nomes → jogo → resultado**. A navegação apenas alterna seções; não há roteador.

- Estrutura visual: `index.html`; estilos nos arquivos de `css/`, conforme a responsabilidade.
- Campos e validação dos nomes: `js/ui/jogadores.js`.
- Navegação, seleção das células e eventos: `js/app.js`.
- Endereço do backend: `js/config.js`.
- Transporte HTTP: `js/services/api.js`.

O cliente exibe os estados enviados pelo backend. Os nomes são registrados no console junto à quantidade; sua inclusão no corpo da requisição permanece como ponto de integração em `iniciarPartida(nomes)`.

## Organização do CSS

O HTML continua carregando apenas `css/style.css`. Esse arquivo contém os imports em ordem: **base → layout → componentes → telas**. Os imports usam CSS nativo e não exigem compilação.

- `base/`: variáveis do tema, normalização, tipografia e acessibilidade globais.
- `layout/`: estrutura compartilhada entre as telas.
- `components/`: elementos reutilizáveis e seus estados de interação.
- `pages/`: regras específicas de cada seção da SPA; não são páginas HTML separadas.

Mantenha as media queries junto às regras do componente ou da tela correspondente. As animações também ficam com o componente que as utiliza; a preferência global de movimento reduzido fica em `base/global.css`.

Ao criar um novo arquivo, adicione seu import ao grupo correspondente em `style.css`. Evite colocar regras diretamente nesse arquivo de entrada ou duplicar estilos compartilhados nos arquivos das telas. Os arquivos usam indentação de dois espaços e uma declaração por linha.

## Contrato da API

O fluxo da interface é coberto por [testes Cypress com relatório Mochawesome](../cypress/README.md).
As respostas controladas desses testes ficam fora de `static/`; executar o frontend
normalmente continua dependendo da API real.

Em `js/config.js`, `API_BASE = ""` usa a mesma origem; para outro servidor, configure o endereço e permita a origem do front-end no CORS do backend.

| Método | Endpoint | Corpo | Resposta |
| --- | --- | --- | --- |
| POST | `/partida` | `{ "num_jogadores": 2 }` | Estado completo |
| POST | `/partida/<id>/dica` | `{ "dica": "cruzeiro" }` | Estado completo |
| POST | `/partida/<id>/palpite` | `{ "palpite": "A3" }` | Estado completo |
| GET | `/partida/<id>/placar` | — | `{ "acertos": 1, "erros": 0 }` |

Erros HTTP podem retornar `{ "erro": "Mensagem para o jogador" }`.

O estado completo contém `id`, `fase` (`dica`, `palpite` ou `final`), `jogador_dica`, `carta_secreta`, `dica`, `tabuleiro` e `placar`. Os textos `mensagem` e `resumo` são opcionais.

O tabuleiro contém `linhas` e `colunas` com `id` e `palavra`, além de `celulas` com `coordenada` e `estado` (`vazia` ou `acerto`).

A interface usa uma tela compartilhada. A API deve enviar a carta secreta apenas na fase de dica. Uma versão em dispositivos separados também precisa de autenticação e filtragem dos dados privados no backend.
