import test, { beforeEach } from "node:test";
import assert from "node:assert/strict";
import { instalarDomFalso } from "./helpers/dom-falso.mjs";
import {
  criarCelula, criarCabecalho, criarLinha, renderizarTabuleiro, atualizarSelecao,
  selecionarCelula, obterCelulaSelecionada, obterCelulaParaFoco, vincularSelecao
} from "../static/js/ui/tabuleiro.js";

const tabuleiro = {
  linhas: [{ id: "A", palavra: "mar" }, { id: "B", palavra: "casa" }],
  colunas: [{ id: "1", palavra: "noite" }, { id: "2", palavra: "festa" }],
  celulas: [
    { coordenada: "A1", estado: "vazia" }, { coordenada: "A2", estado: "acerto" },
    { coordenada: "B1", estado: "vazia" }, { coordenada: "B2", estado: "vazia" }
  ]
};

let dom;
beforeEach(() => { dom = instalarDomFalso(); });

const grade = () => dom.get("tabuleiro");
const botoes = () => grade().querySelectorAll("button[data-coordenada]");
const botao = (c) => botoes().find((b) => b.dataset.coordenada === c);

test("criarCelula usa textContent e acrescenta o detalhe em <small>", () => {
  const celula = criarCelula("<b>x</b>", "celula-cabecalho", "rowheader", "<i>y</i>");
  assert.equal(celula.tagName, "DIV");
  assert.equal(celula.className, "celula celula-cabecalho");
  assert.equal(celula.getAttribute("role"), "rowheader");
  assert.equal(celula.children[0].tagName, "SMALL");
  assert.equal(celula.textContent, "<b>x</b><i>y</i>");
  assert.equal(celula.children.length, 1);
});

test("criarCabecalho: canto + uma célula por coluna, com papéis de cabeçalho", () => {
  const cab = criarCabecalho(tabuleiro.colunas);
  assert.equal(cab.className, "linha-tabuleiro");
  assert.equal(cab.getAttribute("role"), "row");
  assert.equal(cab.children.length, 3);
  assert.ok(cab.children[0].classList.contains("celula-canto"));
  assert.equal(cab.children[0].textContent, "↓ linha" + "coluna →");
  assert.deepEqual(cab.children.slice(1).map((c) => c.getAttribute("role")), ["columnheader", "columnheader"]);
  assert.deepEqual(cab.children.slice(1).map((c) => c.textContent), ["1noite", "2festa"]);
});

test("criarLinha: rowheader, botão aninhado em cell e acerto direto como cell", () => {
  const celulas = new Map(tabuleiro.celulas.map((c) => [c.coordenada, c]));
  const faixa = criarLinha(tabuleiro.linhas[0], tabuleiro.colunas, celulas, new Set());
  assert.equal(faixa.getAttribute("role"), "row");
  assert.equal(faixa.children[0].getAttribute("role"), "rowheader");
  const [, vazia, acerto] = faixa.children;
  assert.equal(vazia.className, "espaco-celula");
  assert.equal(vazia.getAttribute("role"), "cell");
  const b = vazia.children[0];
  assert.equal(b.tagName, "BUTTON");
  assert.equal(b.type, "button");
  assert.equal(b.getAttribute("aria-pressed"), "false");
  assert.equal(b.getAttribute("aria-label"), "Selecionar coordenada A1: mar e noite");
  assert.equal(acerto.tagName, "DIV");
  assert.equal(acerto.getAttribute("role"), "cell");
  assert.equal(acerto.dataset.coordenada, "A2");
  assert.equal(acerto.getAttribute("aria-label"), "Carta posicionada em A2: mar e festa");
  assert.equal(acerto.textContent, "A2✓ acerto");
});

test("acertos novos recebem novo-acerto; os já conhecidos não", () => {
  const celulas = new Map(tabuleiro.celulas.map((c) => [c.coordenada, c]));
  const novo = criarLinha(tabuleiro.linhas[0], tabuleiro.colunas, celulas, new Set()).children[2];
  const antigo = criarLinha(tabuleiro.linhas[0], tabuleiro.colunas, celulas, new Set(["A2"])).children[2];
  assert.equal(novo.className, "celula celula-acerto novo-acerto");
  assert.equal(antigo.className, "celula celula-acerto");
});

test("renderizarTabuleiro: 1 cabeçalho + 1 linha por linha do tabuleiro", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  assert.equal(grade().children.length, 3);
  assert.ok(grade().children.every((f) => f.getAttribute("role") === "row"));
  assert.equal(botoes().length, 3);
  assert.deepEqual(botoes().map((b) => b.dataset.coordenada), ["A1", "B1", "B2"]);
});

test("renderizarTabuleiro substitui o conteúdo anterior e descarta a seleção", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  selecionarCelula("A1", true);
  renderizarTabuleiro(tabuleiro, new Set(), true);
  assert.equal(grade().children.length, 3);
  assert.equal(obterCelulaSelecionada(), null);
  assert.equal(dom.get("selecao-palpite").textContent, "Nenhuma coordenada selecionada.");
});

test("fora da fase de palpite: células e confirmação ficam desabilitadas", () => {
  renderizarTabuleiro(tabuleiro, new Set(), false);
  assert.ok(botoes().every((b) => b.disabled));
  assert.equal(dom.get("confirmar-palpite").disabled, true);
  assert.equal(obterCelulaParaFoco(), null);
});

test("selecionar habilita a confirmação e anuncia a coordenada", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  assert.equal(dom.get("confirmar-palpite").disabled, true);
  selecionarCelula("B1", true);
  assert.equal(obterCelulaSelecionada().dataset.coordenada, "B1");
  assert.equal(botao("B1").getAttribute("aria-pressed"), "true");
  assert.equal(dom.get("confirmar-palpite").disabled, false);
  assert.equal(dom.get("selecao-palpite").textContent, "Coordenada selecionada: B1.");
});

test("seleção única: escolher outra célula desmarca a anterior", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  selecionarCelula("A1", true);
  selecionarCelula("B2", true);
  assert.equal(grade().querySelectorAll(".celula-selecionada").length, 1);
  assert.equal(botao("A1").getAttribute("aria-pressed"), "false");
  assert.equal(botao("B2").getAttribute("aria-pressed"), "true");
});

test("repetir a seleção da mesma coordenada limpa o palpite", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  selecionarCelula("A1", true);
  selecionarCelula("A1", true);
  assert.equal(obterCelulaSelecionada(), null);
  assert.equal(botao("A1").getAttribute("aria-pressed"), "false");
  assert.equal(dom.get("confirmar-palpite").disabled, true);
  assert.equal(dom.get("selecao-palpite").textContent, "Nenhuma coordenada selecionada.");
});

test("negativo: seleção ignorada se ocupado/fase errada, coordenada inexistente ou acerto", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  selecionarCelula("A1", false);
  selecionarCelula("Z9", true);
  selecionarCelula("A2", true); // acerto não é botão
  assert.equal(obterCelulaSelecionada(), null);
});

test("negativo: célula desabilitada não pode ser selecionada", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  botao("A1").disabled = true;
  selecionarCelula("A1", true);
  assert.equal(obterCelulaSelecionada(), null);
});

test("atualizarSelecao(false) desabilita tudo e mantém a marcação existente", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  selecionarCelula("B1", true);
  atualizarSelecao(false);
  assert.ok(botoes().every((b) => b.disabled));
  assert.equal(dom.get("confirmar-palpite").disabled, true);
  assert.equal(obterCelulaSelecionada().dataset.coordenada, "B1");
  atualizarSelecao(true);
  assert.equal(dom.get("confirmar-palpite").disabled, false);
});

test("foco: prioriza a célula selecionada; senão, a primeira habilitada", () => {
  renderizarTabuleiro(tabuleiro, new Set(), true);
  assert.equal(obterCelulaParaFoco().dataset.coordenada, "A1");
  selecionarCelula("B2", true);
  assert.equal(obterCelulaParaFoco().dataset.coordenada, "B2");
});

test("vincularSelecao: delegação cobre botões renderizados depois e ignora outros alvos", () => {
  const chamadas = [];
  vincularSelecao((c) => chamadas.push(c));
  renderizarTabuleiro(tabuleiro, new Set(), true);
  grade().disparar("click", { target: botao("B2") });
  grade().disparar("click", { target: grade().children[0] });
  grade().disparar("click", { target: grade().children[1].children[2] }); // acerto
  assert.deepEqual(chamadas, ["B2"]);
});