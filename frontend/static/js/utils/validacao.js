/* Valida o formato das respostas do backend, sem decidir regras de jogo. */
export function validarPlacar(placar) {
  if (!placar || ![placar.acertos, placar.erros].every((valor) => Number.isInteger(valor) && valor >= 0)) {
    throw new Error("O placar recebido da API é inválido.");
  }
}

export function validarEstado(dados) {
  validarPlacar(dados?.placar);
  if (!dados.id || !["dica", "palpite", "final"].includes(dados.fase)) throw new Error("Estado de partida inválido na resposta da API.");
  const tabuleiro = dados.tabuleiro;
  if (!tabuleiro || ![tabuleiro.linhas, tabuleiro.colunas, tabuleiro.celulas].every(Array.isArray)
    || !tabuleiro.linhas.length || !tabuleiro.colunas.length
    || ![...tabuleiro.linhas, ...tabuleiro.colunas].every((eixo) => eixo && typeof eixo.id === "string" && typeof eixo.palavra === "string")
    || !tabuleiro.celulas.every((celula) => celula && typeof celula.coordenada === "string" && ["vazia", "acerto"].includes(celula.estado))) {
    throw new Error("O tabuleiro recebido não segue o contrato descrito em static/README.md.");
  }
  if (dados.fase === "dica" && typeof dados.carta_secreta !== "string") throw new Error("A API não enviou a carta para quem dá a dica.");
  if (dados.fase === "palpite" && typeof dados.dica !== "string") throw new Error("A API não enviou a dica da rodada.");
}

