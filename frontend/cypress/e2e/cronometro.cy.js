// Tempo total e resultado: relógio e API simulados, sem limite por carta.
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

const desempenho = (concluida = true) => ({
  classificacao: "Bom", concluida, cartas_restantes: concluida ? 0 : 3,
  total_cartas: 9,
});

describe("Tempo livre da partida e desempenho", () => {
  beforeEach(() => {
    cy.fixture("partida").as("base");
    cy.clock();
  });

  it("conta todo o tempo sem descartar cartas ou enviar requisição de expiração", function () {
    cy.intercept("POST", `${rota}/tempo`, {statusCode: 500}).as("tempo");
    iniciar({ ...this.base, duracao_segundos: 65 });
    cy.get("#tempo-total").should("contain.text", "01:05");
    cy.get("#dica").type("ponte");
    cy.tick(3600000);
    cy.get("#tempo-total").should("contain.text", "61:05");
    cy.get("#dica").should("have.value", "ponte");
    cy.get("#cronometro").should("not.exist");
    cy.get("@tempo.all").should("have.length", 0);
    cy.get("#erros").should("have.text", "0");
    cy.get("#resultado-palpite").should("not.be.visible");
  });

  [205, 301].forEach((duracao) => {
    it(`mostra classificação sem limite de tempo ao concluir em ${duracao}s e congela o relógio final`, function () {
      const palpite = { ...this.base, fase: "palpite", carta_secreta: null, dica: "ponte", duracao_segundos: 100 };
      const final = { ...palpite, fase: "final", dica: null, duracao_segundos: duracao,
        placar: { acertos: 7, erros: 2 }, desempenho: desempenho(), resumo: "Partida encerrada." };
      cy.intercept("POST", `${rota}/dica`, { body: palpite }).as("dica");
      cy.intercept("POST", `${rota}/palpite`, { body: final }).as("palpite");
      iniciar({ ...this.base, duracao_segundos: 0 });
      cy.get("#dica").type("ponte");
      cy.get('#form-dica button[type="submit"]').click();
      cy.wait("@dica");
      cy.get("#tempo-total").should("contain.text", "01:40");
      cy.get('button[data-coordenada="A3"]').click();
      cy.get("#confirmar-palpite").click();
      cy.wait("@palpite");
      cy.get("#continuar-palpite").click();
      cy.get("#classificacao-final").should("have.text", "Bom");
      cy.get("#ritmo-final").should("not.exist");
      cy.get("#desempenho-final").should("not.contain.text", "5 minutos");
      const esperado = duracao === 205 ? "03:25" : "05:01";
      cy.get("#duracao-final").should("contain.text", esperado);
      cy.tick(60000);
      cy.get("#duracao-final").should("contain.text", esperado);
      if (duracao === 205) {
        [[1280, 900, "desktop"], [390, 844, "celular"]].forEach(([largura, altura, nome]) => {
          cy.viewport(largura, altura);
          cy.document().then((doc) => expect(doc.documentElement.scrollWidth).to.be.at.most(largura));
          cy.screenshot(`desempenho-${nome}`, { capture: "fullPage" });
        });
      }
      cy.get("#jogar-novamente").click();
      cy.get("#tela-inicial").should("be.visible");
    });
  });

  it("identifica resultado parcial no encerramento antecipado", function () {
    iniciar({ ...this.base, duracao_segundos: 0 });
    cy.intercept("POST", `${rota}/encerrar`, { body: {
      ...this.base, fase: "final", carta_secreta: null, duracao_segundos: 90,
      placar: { acertos: 6, erros: 0 }, desempenho: desempenho(false),
    }}).as("encerrar");
    cy.get("#encerrar-jogo").click();
    cy.wait("@encerrar");
    cy.get("#classificacao-final").should("have.text", "Resultado parcial: Bom");
    cy.get("#cartas-restantes").should("contain.text", "3 de 9");
    cy.get("#ritmo-final").should("not.exist");
  });
});
