describe("Interface da partida: validação, erros e resultado", () => {
  function abrirNomes() {
    cy.visit("/");
    cy.get('#form-iniciar button[type="submit"]').click();
    cy.get("#tela-nomes-jogadores").should("be.visible");
  }

  function iniciarComResposta(estado) {
    cy.intercept("POST", "/partida", { statusCode: 201, body: estado }).as("iniciar");
    abrirNomes();
    cy.get("#nome-jogador-1").type("Ana");
    cy.get("#nome-jogador-2").type("Henrique");
    cy.get("#comecar-jogo").click();
    cy.wait("@iniciar").its("request.body").should("deep.equal", { num_jogadores: 2 });
    cy.get("#tela-jogo").should("be.visible");
  }

  it("sem mock: abre os campos de nomes conforme a quantidade de jogadores", () => {
    cy.visit("/");
    cy.get("#jogadores").clear().type("3");
    cy.get('#form-iniciar button[type="submit"]').click();
    cy.get("#tela-nomes-jogadores").should("be.visible");
    cy.get("#campos-nomes input").should("have.length", 3);
    cy.get('#campos-nomes label[for="nome-jogador-3"]').should("contain.text", "Jogador 3");
  });

  it("sem mock, negativo: bloqueia nome vazio e mostra o erro", () => {
    abrirNomes();
    cy.get("#nome-jogador-1").type("Ana");
    cy.get("#comecar-jogo").click();
    cy.get("#erro-nomes").should("be.visible").and("contain.text", "Preencha o nome");
    cy.get("#nome-jogador-2").should("have.attr", "aria-invalid", "true");
    cy.get("#tela-nomes-jogadores").should("be.visible");
    cy.get("#tela-jogo").should("not.be.visible");
  });

  it("com mock: mostra o erro HTTP 500 ao iniciar e permite nova tentativa", () => {
    cy.intercept("POST", "/partida", {
      statusCode: 500,
      body: { erro: "Servidor indisponível. Tente novamente." }
    }).as("erroInicio");
    abrirNomes();
    cy.get("#nome-jogador-1").type("Ana");
    cy.get("#nome-jogador-2").type("Henrique");
    cy.get("#comecar-jogo").click();
    cy.wait("@erroInicio").its("response.statusCode").should("equal", 500);
    cy.get("#erro").should("be.visible").and("have.text", "Servidor indisponível. Tente novamente.");
    cy.get("#tela-nomes-jogadores").should("be.visible");
    cy.get("#comecar-jogo").should("be.enabled");
  });

  it("com mock: mostra a tela final e o placar após a vitória", () => {
    cy.fixture("partida").then((estado) => {
      const caminho = `/partida/${estado.id}`;
      const palpite = { ...estado, fase: "palpite", carta_secreta: null, dica: "cruzeiro" };
      const vitoria = {
        ...palpite,
        fase: "final",
        placar: { acertos: 1, erros: 0 },
        resumo: "Vitória da equipe!",
        tabuleiro: {
          ...estado.tabuleiro,
          celulas: estado.tabuleiro.celulas.map((celula) =>
            celula.coordenada === "A3" ? { ...celula, estado: "acerto" } : celula)
        }
      };
      cy.intercept("POST", `${caminho}/dica`, { statusCode: 200, body: palpite }).as("dica");
      cy.intercept("POST", `${caminho}/palpite`, { statusCode: 200, body: vitoria }).as("vitoria");
      iniciarComResposta(estado);
      cy.get("#tabuleiro [data-coordenada]").should("have.length", 9);
      cy.get("#dica").type("cruzeiro");
      cy.get('#form-dica button[type="submit"]').click();
      cy.wait("@dica").its("request.body").should("deep.equal", { dica: "cruzeiro" });
      cy.get('button[data-coordenada="A3"]').click();
      cy.get("#confirmar-palpite").click();
      cy.wait("@vitoria").its("request.body").should("deep.equal", { palpite: "A3" });
      cy.get("#tela-final").should("be.visible");
      cy.get("#tela-jogo").should("not.be.visible");
      cy.get("#acertos-finais").should("have.text", "1");
      cy.get("#erros-finais").should("have.text", "0");
      cy.get("#resumo-final").should("have.text", "Vitória da equipe!");
    });
  });
});
