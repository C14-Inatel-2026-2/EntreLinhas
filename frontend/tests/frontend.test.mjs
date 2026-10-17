import test from "node:test";
import assert from "node:assert/strict";
import { validarEstado, validarPlacar } from "../static/js/utils/validacao.js";
import { chamarAPI } from "../static/js/services/api.js";

const estado = {
  id: "partida-1",
  fase: "dica",
  carta_secreta: "A1",
  placar: { acertos: 0, erros: 0 },
  tabuleiro: {
    linhas: [{ id: "A", palavra: "mar" }],
    colunas: [{ id: "1", palavra: "viagem" }],
    celulas: [{ coordenada: "A1", estado: "vazia" }]
  }
};

test("sem mock: validarPlacar aceita pontuação inteira e não negativa", () => {
  assert.doesNotThrow(() => validarPlacar({ acertos: 2, erros: 1 }));
  assert.throws(() => validarPlacar({ acertos: -1, erros: 0 }), /placar recebido/);
});

test("sem mock: validarEstado rejeita tabuleiro com célula inválida", () => {
  assert.doesNotThrow(() => validarEstado(estado));
  const invalido = {
    ...estado,
    tabuleiro: { ...estado.tabuleiro, celulas: [{ coordenada: "A1", estado: "desconhecido" }] }
  };
  assert.throws(() => validarEstado(invalido), /tabuleiro recebido/);
});

test("com mock: chamarAPI envia JSON e devolve a resposta válida", async (t) => {
  const chamadas = [];
  t.mock.method(globalThis, "fetch", async (url, opcoes) => {
    chamadas.push({ url, opcoes });
    return { ok: true, json: async () => estado };
  });

  assert.deepEqual(await chamarAPI("/partida", "POST", { num_jogadores: 2 }), estado);
  assert.equal(chamadas.length, 1);
  assert.equal(chamadas[0].url, "/partida");
  assert.equal(chamadas[0].opcoes.method, "POST");
  assert.deepEqual(JSON.parse(chamadas[0].opcoes.body), { num_jogadores: 2 });
});

test("com mock, negativo: chamarAPI informa o erro HTTP 500 da API", async (t) => {
  t.mock.method(globalThis, "fetch", async () => ({
    ok: false,
    status: 500,
    json: async () => ({ erro: "Servidor indisponível. Tente novamente." })
  }));

  await assert.rejects(
    chamarAPI("/partida", "POST", { num_jogadores: 2 }),
    { message: "Servidor indisponível. Tente novamente." }
  );
});
