describe("Diálogos: abertura, fechamento e foco", () => {
  function iniciar(estado) {
    cy.intercept("POST", "/partida", { body: estado });
    cy.visit("/");
    cy.get('#form-iniciar button[type="submit"]').click();
    cy.get("#nome-jogador-1").type("Ana");
    cy.get("#nome-jogador-2").type("Bia");
    cy.get("#comecar-jogo").click();
    cy.get("#inicio-turno").should("be.visible");
    cy.get("#continuar-turno").should("be.focused");
  }

  it("devolve o foco à carta ao fechar o diálogo inicial com Escape", () => {
    cy.fixture("partida").then((estado) => {
      iniciar(estado);
      cy.get("#continuar-turno").type("{esc}");
      cy.get("#inicio-turno").should("not.be.visible");
      cy.get("#revelar-carta").should("be.focused");
    });
  });

  for (const acertou of [true, false]) {
    for (const final of [true, false]) {
      it(`${acertou ? "acerto" : "erro"}: restaura o foco ${final ? "no resultado final" : "na rodada seguinte"}`, () => {
        cy.fixture("partida").then((estado) => {
          const caminho = `/partida/${estado.id}`;
          cy.intercept("POST", `${caminho}/dica`, {
            body: { ...estado, fase: "palpite", carta_secreta: null, dica: "ponte" }
          });
          cy.intercept("POST", `${caminho}/palpite`, {
            body: {
              ...estado,
              fase: final ? "final" : "dica",
              placar: { acertos: acertou ? 1 : 0, erros: acertou ? 0 : 1 }
            }
          });
          iniciar(estado);
          cy.get("#continuar-turno").click();
          cy.get("#revelar-carta").should("be.focused");
          cy.get("#dica").type("ponte");
          cy.get('#form-dica button[type="submit"]').click();
          cy.get('button[data-coordenada="A1"]').click();
          cy.get("#confirmar-palpite").click();
          cy.get("#resultado-palpite").should("be.visible")
            .and("have.attr", "data-resultado", acertou ? "acerto" : "erro");
          cy.get("#titulo-palpite").should("have.text", acertou ? "Acertou!" : "Errou!");
          cy.get("#continuar-palpite").should("be.focused")
            .and("have.text", final ? "Ver resultado" : "Continuar");
          if (acertou) cy.get("#continuar-palpite").click();
          else cy.get("#continuar-palpite").type("{esc}");
          cy.get("#resultado-palpite").should("not.be.visible");
          cy.get(final ? "#titulo-final" : "#revelar-carta").should("be.focused");
        });
      });
    }
  }
});
