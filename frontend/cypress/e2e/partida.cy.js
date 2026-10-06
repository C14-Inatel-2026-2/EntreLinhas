// Dados simulados somente para navegar entre as telas; as verificações são de interface.
const rota = "/partida/partida-teste";

function abrirNomes(quantidade = 2) {
  cy.get("#jogadores").clear().type(String(quantidade));
  cy.get('#form-iniciar button[type="submit"]').click();
  cy.get("#tela-nomes-jogadores").should("be.visible");
  cy.get("#campos-nomes input").should("have.length", quantidade);
}

function preencherNomes(nomes = ["Ana", "Henrique"]) {
  nomes.forEach((nome, indice) => {
    cy.get(`#nome-jogador-${indice + 1}`).clear().type(nome);
  });
}

function interceptarInicio(estado) {
  cy.intercept("POST", "/partida", { statusCode: 201, body: estado }).as("iniciar");
}

function iniciar(estado) {
  interceptarInicio(estado);
  abrirNomes();
  preencherNomes();
  cy.get("#comecar-jogo").click();
  cy.wait("@iniciar");
  cy.get("#tela-jogo").should("be.visible");
}

function enviarDica(estado, dica = "cruzeiro") {
  cy.intercept("POST", `${rota}/dica`, {
    body: { ...estado, fase: "palpite", carta_secreta: null, dica }
  }).as("dica");
  cy.get("#dica").type(dica);
  cy.get('#form-dica button[type="submit"]').click();
  cy.wait("@dica");
  cy.get("#form-palpite").should("be.visible");
  cy.get("#dica-atual").should("have.text", dica);
  cy.get("#carta-secreta").should("not.be.visible").and("have.text", "");
}

describe("Interface web — navegação e interação com Cypress", () => {
  beforeEach(() => {
    cy.addTestContext("Escopo: telas, formulários e interações no navegador. Dados simulados permitem navegar entre etapas; não há verificações de API, regras Python ou SQLite.");
    cy.fixture("partida").as("estado");
    cy.visit("/");
    cy.get("#tela-inicial").should("be.visible");
  });

  for (const [tela, largura, altura] of [["desktop", 1280, 900], ["celular", 390, 844]]) {
    it(`percorre início, nomes, dica, seleção de palpite e resultado no ${tela}`, function () {
      cy.viewport(largura, altura);
      iniciar(this.estado);
      cy.get("#turno").should("contain.text", "Ana dá a dica");
      cy.get("#tabuleiro [data-coordenada]").should("have.length", 9);
      cy.get("#tabuleiro button").should("be.disabled");
      cy.get("#carta-secreta").should("not.be.visible");
      cy.get("#revelar-carta").click();
      cy.get("#carta-secreta").should("be.visible").and("contain.text", "A3");
      cy.get("#revelar-carta").click();
      cy.get("#carta-secreta").should("not.be.visible").and("have.text", "");

      enviarDica(this.estado);
      cy.get("#turno").should("contain.text", "Henrique, é sua vez de dar o palpite!");
      cy.get("#jogador-palpite").should("contain.text", "Henrique confirma o palpite");
      cy.get("#confirmar-palpite").should("be.disabled");
      cy.get('[data-coordenada="A1"]').click();
      cy.get('[data-coordenada="A1"]').should("have.attr", "aria-pressed", "true");
      cy.get('[data-coordenada="A3"]').click();
      cy.get('[data-coordenada="A1"]').should("have.attr", "aria-pressed", "false");
      cy.get(".celula-selecionada").should("have.length", 1).and("have.attr", "data-coordenada", "A3");

      const segundaRodada = {
        ...this.estado,
        jogador_dica: 2,
        carta_secreta: "B2",
        placar: { acertos: 1, erros: 0 },
        tabuleiro: {
          ...this.estado.tabuleiro,
          celulas: this.estado.tabuleiro.celulas.map((celula) =>
            celula.coordenada === "A3" ? { ...celula, estado: "acerto" } : celula)
        }
      };
      cy.intercept("POST", `${rota}/palpite`, { body: segundaRodada }).as("acertar");
      cy.get("#confirmar-palpite").click();
      cy.wait("@acertar");
      cy.get("#resultado-palpite").should("be.visible").and("have.attr", "data-resultado", "acerto");
      cy.get("#titulo-palpite").should("have.text", "Acertou!");
      cy.get("#continuar-palpite").should("have.focus");
      cy.screenshot(`popup-acerto-${tela}`, { capture: "viewport" });
      cy.get("#continuar-palpite").click();
      cy.get("#resultado-palpite").should("not.be.visible");
      cy.get("#revelar-carta").should("have.focus");
      cy.get("#acertos").should("have.text", "1");
      cy.get("#erros").should("have.text", "0");
      cy.get('[data-coordenada="A3"]').should("have.class", "celula-acerto");
      cy.get('button[data-coordenada="A3"]').should("not.exist");
      cy.get("#turno").should("contain.text", "Henrique dá a dica");

      enviarDica(segundaRodada, "aniversário");
      cy.get("#turno").should("contain.text", "Ana, é sua vez de dar o palpite!");
      const resultado = {
        ...segundaRodada,
        fase: "final",
        carta_secreta: null,
        placar: { acertos: 1, erros: 1 },
        resumo: "Partida encerrada: 1 carta posicionada e 1 descartada."
      };
      cy.intercept("POST", `${rota}/palpite`, { body: resultado }).as("errar");
      cy.get('[data-coordenada="B1"]').click();
      cy.get("#confirmar-palpite").click();
      cy.wait("@errar");
      cy.get("#resultado-palpite").should("be.visible").and("have.attr", "data-resultado", "erro");
      cy.get("#titulo-palpite").should("have.text", "Errou!");
      cy.get("#continuar-palpite").should("have.text", "Ver resultado");
      cy.screenshot(`popup-erro-${tela}`, { capture: "viewport" });
      cy.get("#continuar-palpite").should("have.focus").type("{esc}");
      cy.get("#resultado-palpite").should("not.be.visible");
      cy.get("#titulo-final").should("have.focus");
      cy.get("#tela-final").should("be.visible");
      cy.get("#tela-jogo").should("not.be.visible");
      cy.get("#acertos-finais").should("have.text", "1");
      cy.get("#erros-finais").should("have.text", "1");
      cy.get("#resumo-final").should("have.text", resultado.resumo);
      cy.screenshot(`resultado-${tela}`, { capture: "viewport" });
      cy.get("#jogar-novamente").click();
      cy.get("#tela-inicial").should("be.visible");
      cy.get("#tela-final").should("not.be.visible");
    });
  }

  it("impede iniciar com menos de dois ou mais de seis jogadores", () => {
    for (const quantidade of [1, 7]) {
      cy.get("#jogadores").clear().type(String(quantidade));
      cy.get('#form-iniciar button[type="submit"]').click();
      cy.get("#jogadores").should(($campo) => expect($campo[0].checkValidity()).to.equal(false));
      cy.get("#tela-inicial").should("be.visible");
      cy.get("#tela-nomes-jogadores").should("not.be.visible");
    }
  });

  it("bloqueia nomes vazios e preserva nomes ao mudar a quantidade", function () {
    interceptarInicio(this.estado);
    abrirNomes();
    cy.get("#nome-jogador-1").type("Ana");
    cy.get("#nome-jogador-2").type("   ");
    cy.get("#comecar-jogo").should("have.attr", "aria-disabled", "true").click();
    cy.get("#erro-nomes").should("be.visible");
    cy.get("#nome-jogador-2").should("have.attr", "aria-invalid", "true");
    cy.get("#tela-nomes-jogadores").should("be.visible");
    cy.get("#voltar-nomes").click();
    abrirNomes(6);
    cy.get("#nome-jogador-1").should("have.value", "Ana");
    preencherNomes(["Ana", "Henrique", "Caio", "Mateus", "Lia", "Bia"]);
    cy.get("#comecar-jogo").should("have.attr", "aria-disabled", "false").click();
    cy.wait("@iniciar");
    cy.get("#tela-jogo").should("be.visible");
  });

  it("bloqueia dica vazia ou com espaços e permite desmarcar o palpite", function () {
    iniciar(this.estado);
    cy.get('#form-dica button[type="submit"]').click();
    cy.get("#dica").should(($campo) => expect($campo[0].checkValidity()).to.equal(false));
    cy.get("#dica").type("duas palavras");
    cy.get('#form-dica button[type="submit"]').click();
    cy.get("#form-dica").should("be.visible");
    cy.get("#dica").should(($campo) => expect($campo[0].checkValidity()).to.equal(false));
    cy.get("#dica").clear();
    enviarDica(this.estado);
    cy.get('[data-coordenada="A3"]').click();
    cy.get("#confirmar-palpite").should("be.enabled");
    cy.get('[data-coordenada="A3"]').click();
    cy.get(".celula-selecionada").should("not.exist");
    cy.get("#confirmar-palpite").should("be.disabled");
    cy.get("#selecao-palpite").should("have.text", "Nenhuma coordenada selecionada.");
  });

  for (const [tela, largura, altura] of [["desktop", 1280, 900], ["celular", 390, 844]]) {
    for (const fase of ["dica", "palpite"]) {
      it(`encerra imediatamente na fase de ${fase} no ${tela}`, function () {
        cy.viewport(largura, altura);
        iniciar(this.estado);
        if (fase === "palpite") enviarDica(this.estado);
        const final = { ...this.estado, fase: "final", carta_secreta: null, resumo: "Partida encerrada pelo time." };
        cy.intercept("POST", `${rota}/encerrar`, { body: final }).as("encerrar");
        cy.get("#encerrar-jogo").click();
        cy.wait("@encerrar");
        cy.get("#tela-final").should("be.visible");
        cy.get("#resumo-final").should("have.text", final.resumo);
        cy.get("#acertos-finais").should("have.text", "0");
        cy.get("#erros-finais").should("have.text", "0");
        cy.get("#tela-jogo").should("not.be.visible");
        cy.get("#resultado-palpite").should("not.be.visible");
        cy.get("#jogar-novamente").click();
        cy.get("#tela-inicial").should("be.visible");
      });
    }
  }

  it("mantém a partida e permite tentar novamente quando o encerramento falha", function () {
    iniciar(this.estado);
    cy.intercept("POST", `${rota}/encerrar`, { statusCode: 500, body: { erro: "Não foi possível encerrar." } }).as("falhaEncerrar");
    cy.get("#encerrar-jogo").click();
    cy.wait("@falhaEncerrar");
    cy.get("#erro").should("be.visible").and("have.text", "Não foi possível encerrar.");
    cy.get("#tela-jogo").should("be.visible");
    cy.get("#encerrar-jogo").should("be.enabled").and("have.focus");
    cy.get("#tela-final").should("not.be.visible");
    cy.get("#resultado-palpite").should("not.be.visible");
    cy.intercept("POST", `${rota}/encerrar`, { body: { ...this.estado, fase: "final", carta_secreta: null } }).as("encerrar");
    cy.get("#encerrar-jogo").click();
    cy.wait("@encerrar");
    cy.get("#tela-final").should("be.visible");
  });

  it("não confunde falha da API com palpite errado", function () {
    iniciar(this.estado);
    enviarDica(this.estado);
    cy.intercept("POST", `${rota}/palpite`, { statusCode: 500, body: { erro: "Servidor indisponível." } }).as("falhaPalpite");
    cy.get('button[data-coordenada="A3"]').click();
    cy.get("#confirmar-palpite").click();
    cy.wait("@falhaPalpite");
    cy.get("#erro").should("be.visible").and("have.text", "Servidor indisponível.");
    cy.get("#resultado-palpite").should("not.be.visible");
    cy.get("#form-palpite").should("be.visible");
    cy.get("#confirmar-palpite").should("be.enabled");
    cy.get("#acertos").should("have.text", "0");
    cy.get("#erros").should("have.text", "0");
  });
});
