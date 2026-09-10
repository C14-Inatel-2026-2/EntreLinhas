/* Respostas e sequência fixa da demonstração, isoladas da API real. */
// JSONs ilustrativos: a sequência é fixa e não compara dica ou palpite com a carta.
const TABULEIRO_EXEMPLO = {
  linhas: [{ id: "A", palavra: "mar" }, { id: "B", palavra: "casa" }, { id: "C", palavra: "música" }],
  colunas: [{ id: "1", palavra: "noite" }, { id: "2", palavra: "festa" }, { id: "3", palavra: "viagem" }],
  celulas: [
    { coordenada: "A1", estado: "vazia" }, { coordenada: "A2", estado: "vazia" },
    { coordenada: "A3", estado: "vazia" }, { coordenada: "B1", estado: "vazia" },
    { coordenada: "B2", estado: "vazia" }, { coordenada: "B3", estado: "vazia" },
    { coordenada: "C1", estado: "vazia" }, { coordenada: "C2", estado: "vazia" },
    { coordenada: "C3", estado: "vazia" }
  ]
};
const TABULEIRO_COM_ACERTO = {
  ...TABULEIRO_EXEMPLO,
  celulas: TABULEIRO_EXEMPLO.celulas.map((celula) => celula.coordenada === "A3"
    ? { coordenada: "A3", estado: "acerto" } : celula)
};
const RESPOSTAS_EXEMPLO = [
  { id: "demo", fase: "dica", jogador_dica: 1, carta_secreta: "A3", dica: null,
    tabuleiro: TABULEIRO_EXEMPLO, placar: { acertos: 0, erros: 0 }, mensagem: "Rodada de exemplo 1 de 2. Prepare uma dica!" },
  { id: "demo", fase: "palpite", jogador_dica: 1, carta_secreta: null, dica: "cruzeiro",
    tabuleiro: TABULEIRO_EXEMPLO, placar: { acertos: 0, erros: 0 }, mensagem: "A demonstração usa a dica fixa “cruzeiro”. Passe a tela para os demais." },
  { id: "demo", fase: "dica", jogador_dica: 2, carta_secreta: "B2", dica: null,
    tabuleiro: TABULEIRO_COM_ACERTO, placar: { acertos: 1, erros: 0 }, mensagem: "Acerto ilustrativo em A3! Rodada de exemplo 2 de 2." },
  { id: "demo", fase: "palpite", jogador_dica: 2, carta_secreta: null, dica: "aniversário",
    tabuleiro: TABULEIRO_COM_ACERTO, placar: { acertos: 1, erros: 0 }, mensagem: "A demonstração usa a dica fixa “aniversário”. Passe a tela para os demais." },
  { id: "demo", fase: "final", jogador_dica: 2, carta_secreta: null, dica: null,
    tabuleiro: TABULEIRO_COM_ACERTO, placar: { acertos: 1, erros: 1 }, resumo: "Demonstração concluída: 1 carta posicionada e 1 descartada. Os resultados deste exemplo são fixos." }
];
let indiceMock = 0;

export async function requisitarMock(caminho, metodo) {
  await new Promise((resolver) => setTimeout(resolver, 450));
  if (caminho === "/partida" && metodo === "POST") indiceMock = 0;
  else if (caminho.endsWith("/placar") && metodo === "GET") {
    return structuredClone(RESPOSTAS_EXEMPLO[indiceMock].placar);
  } else {
    const fase = RESPOSTAS_EXEMPLO[indiceMock].fase;
    if (metodo !== "POST" || !caminho.endsWith(`/${fase}`) || fase === "final") {
      throw new Error("Esta ação não está disponível na demonstração.");
    }
    indiceMock += 1;
  }
  return structuredClone(RESPOSTAS_EXEMPLO[indiceMock]);
}

