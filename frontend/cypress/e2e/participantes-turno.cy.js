describe("Participantes do turno", () => {
  for (let quantidade = 2; quantidade <= 6; quantidade += 1) {
    it(`preserva os destaques e textos de dica e palpite com ${quantidade} jogadores`, () => {
      cy.fixture("partida").then((base) => {
        const nomes = ["Ana", "Bia", "Caio", "Davi", "Eva", "Fernando"].slice(0, quantidade);
        const estado = { ...base, num_jogadores: quantidade, jogador_dica: quantidade };
        cy.intercept("POST", "/partida", { body: estado });
        cy.intercept("POST", `/partida/${estado.id}/dica`, {
          body: { ...estado, fase: "palpite", dica: "ponte", carta_secreta: null }
        });
        cy.visit("/");
        cy.get("#jogadores").clear().type(String(quantidade));
        cy.get('#form-iniciar button[type="submit"]').click();
        nomes.forEach((nome, i) => cy.get(`#nome-jogador-${i + 1}`).type(nome));
        cy.get("#comecar-jogo").click();
        cy.get("#nome-inicio-turno").should("have.text", nomes[quantidade - 1]);
        cy.get("#continuar-turno").click();
        cy.get("#nome-turno").should("have.text", nomes[quantidade - 1]);
        cy.get(".jogador-turno-ativo").should("have.length", 1)
          .and("contain.text", nomes[quantidade - 1]).and("contain.text", "Dando a dica");
        cy.get("#dica").type("ponte");
        cy.get('#form-dica button[type="submit"]').click();
        cy.get("#nome-turno").should("have.text", quantidade === 2 ? nomes[0] : "Vez do time");
        cy.get(".jogador-turno-ativo").should("have.length", quantidade - 1)
          .each(($item, i) => {
            cy.wrap($item).should("contain.text", nomes[i]).and("contain.text", "Adivinhando");
          });
        cy.get(".jogador-turno-aguardando").should("have.length", 1)
          .and("contain.text", nomes[quantidade - 1]).and("contain.text", "Aguardando");
        cy.get("#jogador-palpite").should("have.text", quantidade === 2
          ? `${nomes[0]} confirma o palpite.` : "Conversem e confirmem um único palpite para o time.");
      });
    });
  }
});
