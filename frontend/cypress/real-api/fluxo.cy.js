const pagina = `${Cypress.config("baseUrl").replace(":8000", ":5000")}/static/index.html`;

function iniciarPartida(nomes = ["Ana", "Bia"]) {
  cy.visit(pagina);
  cy.get("#jogadores").clear().type(String(nomes.length));
  cy.get('#form-iniciar button[type="submit"]').click();
  nomes.forEach((nome, indice) => cy.get(`#nome-jogador-${indice + 1}`).type(nome));
  cy.get("#comecar-jogo").click();
  cy.get("#tela-jogo").should("be.visible");
}

describe("Interface integrada à API real", () => {
  it("inicia uma partida e renderiza o tabuleiro e o placar", () => {
    iniciarPartida();
    cy.get("#tabuleiro [data-coordenada]").should("have.length", 9);
    cy.get("#acertos").should("have.text", "0");
    cy.get("#erros").should("have.text", "0");
    cy.get("#turno").should("contain.text", "Ana dá a dica");
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
      cy.get("#turno").should("contain.text", "Bia, é sua vez de dar o palpite!");
      cy.get(`button[data-coordenada="${coordenada}"]`).click();
      cy.get("#confirmar-palpite").click();
      cy.get("#titulo-palpite").should("have.text", "Acertou!");
      cy.get("#resultado-palpite").should("be.visible");
      cy.get("#continuar-palpite").click();
      cy.get("#acertos").should("have.text", "1");
      cy.get("#erros").should("have.text", "0");
      cy.get(`[data-coordenada="${coordenada}"]`).should("have.class", "celula-acerto");
      cy.get("#turno").should("contain.text", "Bia dá a dica");
      cy.get("#atualizar-placar").click();
      cy.get("#acertos").should("have.text", "1");
      cy.get("#erro").should("not.be.visible");
    });
  });

  it("alterna os nomes de três jogadores e mostra o último acerto antes do resultado final", () => {
    const nomes = ["Ana", "Bia", "Caio"];
    iniciarPartida(nomes);
    for (let rodada = 0; rodada < 9; rodada += 1) {
      cy.get("#turno").should("contain.text", `${nomes[rodada % 3]} dá a dica`);
      cy.get("#revelar-carta").click();
      cy.get("#carta-secreta").invoke("text").then((texto) => {
        const coordenada = texto.match(/[A-C][1-3]/)[0];
        cy.get("#dica").type("ponte");
        cy.get('#form-dica button[type="submit"]').click();
        cy.get("#form-palpite").should("be.visible");
        cy.get("#turno").should("contain.text", `${nomes[(rodada + 1) % 3]}, é sua vez de dar o palpite!`);
        cy.get(`button[data-coordenada="${coordenada}"]`).click();
        cy.get("#confirmar-palpite").click();
        cy.get("#resultado-palpite").should("be.visible");
        cy.get("#titulo-palpite").should("have.text", "Acertou!");
        cy.get("#continuar-palpite").should("have.text", rodada === 8 ? "Ver resultado" : "Continuar").click();
      });
    }
    cy.get("#tela-final").should("be.visible");
    cy.get("#acertos-finais").should("have.text", "9");
    cy.get("#erros-finais").should("have.text", "0");
    cy.get("#resultado-palpite").should("not.be.visible");
  });

  it("mostra o pop-up de erro e encerra antecipadamente, persistindo o placar", () => {
    iniciarPartida();
    cy.get("#revelar-carta").click();
    cy.get("#carta-secreta").invoke("text").then((texto) => {
      const correta = texto.match(/[A-C][1-3]/)[0];
      const errada = correta === "A1" ? "A2" : "A1";
      cy.get("#dica").type("ponte");
      cy.get('#form-dica button[type="submit"]').click();
      cy.get("#form-palpite").should("be.visible");
      cy.get(`button[data-coordenada="${errada}"]`).click();
      cy.get("#confirmar-palpite").click();
      cy.get("#resultado-palpite").should("be.visible");
      cy.get("#titulo-palpite").should("have.text", "Errou!");
      cy.get("#continuar-palpite").click();
      cy.get("#erros").should("have.text", "1");
      cy.get("#turno").should("contain.text", "Bia dá a dica");
      cy.window().then((janela) => {
        const original = janela.fetch.bind(janela);
        let rotaEncerrar;
        // Espiona a chamada sem interceptar nem substituir a resposta da API.
        cy.spy(janela, "fetch").withArgs(Cypress.sinon.match(/\/encerrar$/)).as("pedidoEncerrar");
        cy.get("#encerrar-jogo").click();
        cy.get("#tela-final").should("be.visible");
        cy.get("#acertos-finais").should("have.text", "0");
        cy.get("#erros-finais").should("have.text", "1");
        cy.get("@pedidoEncerrar").then((pedido) => {
          rotaEncerrar = pedido.firstCall.args[0];
          return original(rotaEncerrar.replace(/\/encerrar$/, ""));
        }).then((resposta) => resposta.json()).then((registro) => {
          expect(registro.data_fim).to.be.a("string");
          expect(registro.pontuacao_final).to.equal(0);
        });
      });
    });
  });
});
