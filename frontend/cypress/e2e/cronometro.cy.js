// Cronômetro da interface. Relógio (cy.clock/cy.tick) e API (cy.intercept) são simulados.
const rota = "/partida/partida-teste";

function iniciar(estado) {
  cy.intercept("POST", "/partida", { statusCode: 201, body: estado }).as("iniciar");
  cy.visit("/");
  cy.get('#form-iniciar button[type="submit"]').click();
  cy.get("#nome-jogador-1").type("Ana");
  cy.get("#nome-jogador-2").type("Henrique");
  cy.get("#comecar-jogo").click();
  cy.wait("@iniciar");
  cy.get("#continuar-turno").click();
}

describe("Cronômetro do turno e tempo total", () => {
  beforeEach(() => {
    cy.fixture("partida").as("base");
    cy.clock(); // antes do cy.visit
  });

  it("com mock: o contador do turno e o tempo total andam com o relógio simulado", function () {
    iniciar({ ...this.base, tempo_restante: 60, duracao_segundos: 65 });
    cy.get("#cronometro").should("contain.text", "60s");
    cy.get("#tempo-total").should("contain.text", "01:05");
    cy.tick(5000);
    cy.get("#cronometro").should("contain.text", "55s");
    cy.get("#tempo-total").should("contain.text", "01:10");
  });

  it("com mock: ao zerar chama /tempo e mostra o popup de tempo esgotado", function () {
    const penalizado = {
      ...this.base, tempo_restante: 60, duracao_segundos: 4, carta_secreta: "B2",
      mensagem: "Tempo esgotado! A carta foi descartada.", placar: { acertos: 0, erros: 1 },
    };
    cy.intercept("POST", `${rota}/tempo`, { body: penalizado }).as("tempo");
    iniciar({ ...this.base, tempo_restante: 3, duracao_segundos: 0 });
    cy.tick(3000);
    cy.wait("@tempo");
    cy.get("#titulo-palpite").should("have.text", "Tempo esgotado!");
    cy.get("#erros").should("have.text", "1");
  });

  it("com mock: a tela final mostra a duração da partida", function () {
    const palpite = { ...this.base, fase: "palpite", carta_secreta: null, dica: "ponte", tempo_restante: 30, duracao_segundos: 100 };
    const final = { ...palpite, fase: "final", dica: null, tempo_restante: null, duracao_segundos: 205,
                    placar: { acertos: 1, erros: 0 }, resumo: "Vitória da equipe!" };
    cy.intercept("POST", `${rota}/dica`, { body: palpite }).as("dica");
    cy.intercept("POST", `${rota}/palpite`, { body: final }).as("palpite");
    iniciar({ ...this.base, tempo_restante: 60, duracao_segundos: 0 });
    cy.get("#dica").type("ponte");
    cy.get('#form-dica button[type="submit"]').click();
    cy.wait("@dica");
    cy.get('button[data-coordenada="A3"]').click();
    cy.get("#confirmar-palpite").click();
    cy.wait("@palpite");
    cy.get("#continuar-palpite").click();
    cy.get("#tela-final").should("be.visible");
    cy.get("#duracao-final").should("contain.text", "03:25");
  });
});