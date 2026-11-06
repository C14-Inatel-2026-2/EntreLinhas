// Cronômetro da interface. Relógio (cy.clock/cy.tick) e API (cy.intercept) são simulados.
const rota = "/partida/partida-teste";

const penalizado = (base) => ({
  ...base, turno: 1, tempo_restante: 60, expira_em: 62, duracao_segundos: 4, carta_secreta: "B2",
  mensagem: "Tempo esgotado! A carta foi descartada.", placar: { acertos: 0, erros: 1 },
});

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
    iniciar({ ...this.base, turno: 0, tempo_restante: 60, expira_em: 62, duracao_segundos: 65 });
    cy.get("#cronometro").should("contain.text", "60s");
    cy.get("#tempo-total").should("contain.text", "01:05");
    cy.tick(5000);
    cy.get("#cronometro").should("contain.text", "55s");
    cy.get("#tempo-total").should("contain.text", "01:10");
  });

  it("com mock: só chama /tempo depois da tolerância e mostra o popup de tempo esgotado", function () {
    cy.intercept("POST", `${rota}/tempo`, { body: penalizado(this.base) }).as("tempo");
    iniciar({ ...this.base, turno: 0, tempo_restante: 3, expira_em: 5, duracao_segundos: 0 });
    cy.tick(3000); // zerou na tela, mas ainda dentro da tolerância
    cy.get("@tempo.all").should("have.length", 0);
    cy.tick(2000);
    cy.wait("@tempo").its("request.body").should("deep.equal", { turno: 0, fase: this.base.fase });
    cy.get("#titulo-palpite").should("have.text", "Tempo esgotado!");
    cy.get("#erros").should("have.text", "1");
  });

  it("com mock: se /tempo falha (HTTP 500), tenta de novo sozinho e aplica o descarte", function () {
    let chamadas = 0;
    cy.intercept("POST", `${rota}/tempo`, (req) => {
      chamadas += 1;
      req.reply(chamadas === 1
        ? { statusCode: 500, body: { erro: "Falha temporária" } }
        : { statusCode: 200, body: penalizado(this.base) });
    }).as("tempo");
    iniciar({ ...this.base, turno: 0, tempo_restante: 3, expira_em: 3, duracao_segundos: 0 });
    cy.tick(3000);
    cy.wait("@tempo");
    cy.get("#erro").should("be.visible");
    cy.tick(2000); // intervalo da nova tentativa
    cy.wait("@tempo");
    cy.get("#titulo-palpite").should("have.text", "Tempo esgotado!");
    cy.get("#erro").should("not.be.visible");
  });

  it("com mock: se zerar durante a consulta lenta do placar, descarta assim que a tela liberar", function () {
    cy.intercept("GET", `${rota}/placar`, { delay: 2000, body: { acertos: 0, erros: 0 } }).as("placar");
    cy.intercept("POST", `${rota}/tempo`, { body: penalizado(this.base) }).as("tempo");
    iniciar({ ...this.base, turno: 0, tempo_restante: 3, expira_em: 3, duracao_segundos: 0 });
    cy.get("#atualizar-placar").click(); // tela ocupada aguardando o placar
    cy.tick(3000);                       // o tempo zera com a tela ocupada
    cy.get("@tempo.all").should("have.length", 0);
    cy.wait("@placar");
    cy.get("#loading").should("not.be.visible");
    cy.tick(500);                        // fim do adiamento, tela livre
    cy.wait("@tempo");
    cy.get("#titulo-palpite").should("have.text", "Tempo esgotado!");
  });

  it("com mock: a tela final mostra a duração da partida", function () {
    const palpite = { ...this.base, turno: 0, fase: "palpite", carta_secreta: null, dica: "ponte", tempo_restante: 30, expira_em: 32, duracao_segundos: 100 };
    const final = { ...palpite, turno: 9, fase: "final", dica: null, tempo_restante: null, expira_em: null, duracao_segundos: 205,
                    placar: { acertos: 1, erros: 0 }, resumo: "Vitória da equipe!" };
    cy.intercept("POST", `${rota}/dica`, { body: palpite }).as("dica");
    cy.intercept("POST", `${rota}/palpite`, { body: final }).as("palpite");
    iniciar({ ...this.base, turno: 0, tempo_restante: 60, expira_em: 62, duracao_segundos: 0 });
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