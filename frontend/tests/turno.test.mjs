import test from "node:test";
import assert from "node:assert/strict";
import { obterParticipantesDoTurno } from "../static/js/utils/turno.js";

const nomes = ["Ana", "Bia", "Caio", "Davi", "Eva", "Fernando"];

for (let quantidade = 2; quantidade <= 6; quantidade += 1) {
  for (let numeroDica = 1; numeroDica <= quantidade; numeroDica += 1) {
    test(`${quantidade} participantes, dica de ${nomes[numeroDica - 1]}: preserva papéis nas três fases`, () => {
      const equipe = Object.freeze(nomes.slice(0, quantidade));
      const autor = equipe[numeroDica - 1];
      const demais = equipe.filter((nome) => nome !== autor);
      for (const fase of ["dica", "palpite", "final"]) {
        const resultado = obterParticipantesDoTurno(equipe, numeroDica, fase);
        assert.equal(resultado.emDupla, quantidade === 2);
        assert.equal(resultado.jogadorDica, autor);
        assert.equal(resultado.jogadorPalpite, quantidade === 2 ? demais[0] : "Vez do time");
        assert.deepEqual(resultado.jogadores.map(({ nome }) => nome), equipe);
        const ativos = resultado.jogadores.filter(({ ativo }) => ativo);
        assert.deepEqual(ativos.map(({ nome }) => nome), fase === "dica" ? [autor] : fase === "palpite" ? demais : []);
        assert.ok(ativos.every(({ situacao }) => situacao === (fase === "dica" ? "Dando a dica" : "Adivinhando")));
        assert.ok(resultado.jogadores.filter(({ ativo }) => !ativo).every(({ situacao }) => situacao === "Aguardando"));
      }
      assert.deepEqual(equipe, nomes.slice(0, quantidade));
    });
  }
}

test("preserva o nome padrão do autor da dica quando os nomes não estão disponíveis", () => {
  assert.equal(obterParticipantesDoTurno([], 2, "dica").jogadorDica, "Jogador 2");
});
