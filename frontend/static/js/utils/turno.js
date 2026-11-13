/* Identifica participantes sem consultar ou alterar o DOM e o estado da SPA. */
export function obterParticipantesDoTurno(nomes, jogadorDica, fase) {
  const emDupla = nomes.length === 2;
  return {
    emDupla,
    jogadorDica: nomes[jogadorDica - 1] || `Jogador ${jogadorDica}`,
    jogadorPalpite: emDupla ? nomes[jogadorDica % nomes.length] : "Vez do time",
    jogadores: nomes.map((nome, indice) => {
      const dandoDica = indice + 1 === jogadorDica;
      const ativo = fase === "dica" ? dandoDica : fase === "palpite" && !dandoDica;
      return {
        nome,
        ativo,
        situacao: ativo ? (fase === "dica" ? "Dando a dica" : "Adivinhando") : "Aguardando"
      };
    })
  };
}
