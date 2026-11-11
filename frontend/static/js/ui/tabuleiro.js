/* Renderização e seleção do tabuleiro, sem depender do estado da navegação. */
import { elemento } from "../utils/dom.js";

const SELETOR_CELULAS = "button[data-coordenada]";

export function criarCelula(texto, classe, papel, detalhe, tag = "div") {
  const celula = document.createElement(tag);
  celula.className = `celula ${classe}`;
  celula.setAttribute("role", papel);
  // textContent mantém palavras e mensagens da API como texto, nunca como HTML.
  celula.textContent = texto;
  if (detalhe) {
    const pequeno = document.createElement("small");
    pequeno.textContent = detalhe;
    celula.append(pequeno);
  }
  return celula;
}

function criarFaixa() {
  const faixa = document.createElement("div");
  faixa.className = "linha-tabuleiro";
  faixa.setAttribute("role", "row");
  return faixa;
}

export function criarCabecalho(colunas) {
  const cabecalho = criarFaixa();
  cabecalho.append(criarCelula("↓ linha", "celula-canto", "columnheader", "coluna →"));
  colunas.forEach((coluna) => cabecalho.append(criarCelula(coluna.id, "celula-cabecalho", "columnheader", coluna.palavra)));
  return cabecalho;
}

function criarCelulaDeCoordenada(linha, coluna, acerto, anteriores) {
  const coordenada = `${linha.id}${coluna.id}`;
  const classe = acerto ? `celula-acerto${anteriores.has(coordenada) ? "" : " novo-acerto"}` : "celula-vazia";
  const celula = criarCelula(coordenada, classe, acerto ? "cell" : "button", acerto ? "✓ acerto" : "", acerto ? "div" : "button");
  celula.dataset.coordenada = coordenada;
  celula.setAttribute("aria-label", `${acerto ? "Carta posicionada em" : "Selecionar coordenada"} ${coordenada}: ${linha.palavra} e ${coluna.palavra}`);
  if (acerto) return celula;
  // O botão nativo responde a Enter/Espaço. O contêiner mantém a semântica da tabela.
  celula.type = "button";
  celula.setAttribute("aria-pressed", "false");
  const espaco = document.createElement("div");
  espaco.className = "espaco-celula";
  espaco.setAttribute("role", "cell");
  espaco.append(celula);
  return espaco;
}

export function criarLinha(linha, colunas, celulas, anteriores) {
  const faixa = criarFaixa();
  faixa.append(criarCelula(linha.id, "celula-cabecalho", "rowheader", linha.palavra));
  colunas.forEach((coluna) => {
    const acerto = celulas.get(`${linha.id}${coluna.id}`)?.estado === "acerto";
    faixa.append(criarCelulaDeCoordenada(linha, coluna, acerto, anteriores));
  });
  return faixa;
}

export function renderizarTabuleiro(tabuleiro, anteriores = new Set(), podeSelecionar = false) {
  const fragmento = document.createDocumentFragment();
  fragmento.append(criarCabecalho(tabuleiro.colunas));
  const celulas = new Map(tabuleiro.celulas.map((celula) => [celula.coordenada, celula]));
  tabuleiro.linhas.forEach((linha) => fragmento.append(criarLinha(linha, tabuleiro.colunas, celulas, anteriores)));
  elemento("tabuleiro").replaceChildren(fragmento);
  atualizarSelecao(podeSelecionar);
}

export function obterCelulaSelecionada() {
  return elemento("tabuleiro").querySelector(`${SELETOR_CELULAS}.celula-selecionada`);
}

export function obterCelulaParaFoco() {
  return elemento("tabuleiro").querySelector(".celula-selecionada")
    || elemento("tabuleiro").querySelector(`${SELETOR_CELULAS}:not(:disabled)`);
}

export function atualizarSelecao(podeSelecionar) {
  elemento("tabuleiro").querySelectorAll(SELETOR_CELULAS).forEach((celula) => {
    celula.disabled = !podeSelecionar;
  });
  const selecionada = obterCelulaSelecionada();
  elemento("confirmar-palpite").disabled = !podeSelecionar || !selecionada;
  elemento("selecao-palpite").textContent = selecionada
    ? `Coordenada selecionada: ${selecionada.dataset.coordenada}.`
    : "Nenhuma coordenada selecionada.";
}

export function selecionarCelula(coordenada, podeSelecionar) {
  if (!podeSelecionar) return;
  const celulas = [...elemento("tabuleiro").querySelectorAll(SELETOR_CELULAS)];
  const alvo = celulas.find((celula) => celula.dataset.coordenada === coordenada);
  if (!alvo || alvo.disabled) return;
  const selecionar = !alvo.classList.contains("celula-selecionada");
  // Uma única seleção; repetir o clique na mesma coordenada limpa o palpite.
  celulas.forEach((celula) => {
    const marcada = celula === alvo && selecionar;
    celula.classList.toggle("celula-selecionada", marcada);
    celula.setAttribute("aria-pressed", String(marcada));
  });
  atualizarSelecao(podeSelecionar);
}

export function vincularSelecao(aoSelecionar) {
  const grade = elemento("tabuleiro");
  
  // Trata cliques do rato
  grade.addEventListener("click", (evento) => {
    const celula = evento.target.closest(SELETOR_CELULAS);
    if (celula && grade.contains(celula)) aoSelecionar(celula.dataset.coordenada);
  });

  // Trata ativação por teclado (Enter ou Espaço) nas células do tabuleiro
  grade.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" || evento.key === " ") {
      const celula = evento.target.closest(SELETOR_CELULAS);
      if (celula && grade.contains(celula)) {
        evento.preventDefault(); // Evita comportamento padrão de scroll com espaço ou submissões indesejadas
        aoSelecionar(celula.dataset.coordenada);
      }
    }
  });
}