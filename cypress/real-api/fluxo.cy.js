const pagina = "http://127.0.0.1:5000/static/index.html";

function iniciarPartida() {
  cy.visit(pagina);
  cy.get('#form-iniciar button[type="submit"]').click();
  cy.get("#nome-jogador-1").type("Ana");
  cy.get("#nome-jogador-2").type("Bia");
  cy.get("#comecar-jogo").click();
  cy.get("#tela-jogo").should("be.visible");
}

describe("Interface integrada à API real", () => {
  it("inicia uma partida e renderiza o tabuleiro e o placar", () => {
    iniciarPartida();
    cy.get("#tabuleiro [data-coordenada]").should("have.length", 9);
    cy.get("#acertos").should("have.text", "0");
    cy.get("#erros").should("have.text", "0");
    cy.get("#turno").should("contain.text", "Jogador 1");
    cy.get("#erro").should("not.be.visible");
  });

  it("envia dica e palpite e atualiza o placar sem interceptação", () => {
    iniciarPartida();
    cy.get("#revelar-carta").click();
    cy.get("#carta-secreta").invoke("text").then((texto) => {
      const coordenada = texto.match(/[A-C][1-3]/)?.[0];
      expect(coordenada).to.be.a("string");
      cy.get("#dica").type("ponte");
      cy.get('#form-dica button[type="submit"]').click();
      cy.get("#form-palpite").should("be.visible");
      cy.get(`button[data-coordenada="${coordenada}"]`).click();
      cy.get("#confirmar-palpite").click();
      cy.get("#acertos").should("have.text", "1");
      cy.get("#erros").should("have.text", "0");
      cy.get(`[data-coordenada="${coordenada}"]`).should("have.class", "celula-acerto");
      cy.get("#turno").should("contain.text", "Jogador 2");
      cy.get("#atualizar-placar").click();
      cy.get("#acertos").should("have.text", "1");
      cy.get("#erro").should("not.be.visible");
    });
  });
});
