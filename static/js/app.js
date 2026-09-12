/* Entrada da SPA: estado da interface, navegação, tabuleiro e eventos de jogo. */
import { chamarAPI } from "./services/api.js";
import { elemento } from "./utils/dom.js";
import { validarPlacar, validarEstado } from "./utils/validacao.js";
import { obterCamposDeNomes, validarNomes, renderizarCamposDeNomes } from "./ui/jogadores.js";

let partida = null;
let ocupado = false;
let telaAtual = "tela-inicial";

function definirLoading(valor) {
  ocupado = valor;
  elemento("loading").hidden = !valor;
  elemento("aplicativo").setAttribute("aria-busy", String(valor));
  document.querySelectorAll("button, input").forEach((controle) => { controle.disabled = valor; });
  atualizarSelecao();
}

async function executarAcao(acao) {
  if (ocupado) return;
  elemento("erro").hidden = true;
  const focoAnterior = document.activeElement;
  definirLoading(true);
  let sucesso = false;
  try {
    await acao();
    sucesso = true;
  } catch (erro) {
    elemento("erro").textContent = erro.message || "Algo deu errado. Tente novamente.";
    elemento("erro").hidden = false;
  } finally {
    definirLoading(false);
    if (sucesso) focarTela();
    else if (focoAnterior && !focoAnterior.closest("[hidden]")) focoAnterior.focus();
  }
}

function mostrarTela(id) {
  document.querySelectorAll(".tela").forEach((tela) => { tela.hidden = tela.id !== id; });
  telaAtual = id;
}

function focarTela() {
  if (telaAtual === "tela-nomes-jogadores") {
    elemento("titulo-nomes").focus();
    return;
  }
  if (telaAtual === "tela-jogo" && partida.fase === "palpite") {
    const celula = elemento("tabuleiro").querySelector(".celula-selecionada")
      || elemento("tabuleiro").querySelector("button[data-coordenada]:not(:disabled)");
    (celula || elemento("titulo-jogo")).focus();
    return;
  }
  const alvo = telaAtual === "tela-jogo"
    ? "revelar-carta"
    : (telaAtual === "tela-final" ? "titulo-final" : "titulo-inicial");
  elemento(alvo).focus();
}

function criarCelula(texto, classe, papel, detalhe, tag = "div") {
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

function renderizarTabuleiro(tabuleiro, anteriores = new Set()) {
  const grade = elemento("tabuleiro");
  const fragmento = document.createDocumentFragment();
  const cabecalho = document.createElement("div");
  cabecalho.className = "linha-tabuleiro";
  cabecalho.setAttribute("role", "row");
  cabecalho.append(criarCelula("↓ linha", "celula-canto", "columnheader", "coluna →"));
  tabuleiro.colunas.forEach((coluna) => cabecalho.append(criarCelula(coluna.id, "celula-cabecalho", "columnheader", coluna.palavra)));
  fragmento.append(cabecalho);
  const celulas = new Map(tabuleiro.celulas.map((celula) => [celula.coordenada, celula]));
  tabuleiro.linhas.forEach((linha) => {
    const faixa = document.createElement("div");
    faixa.className = "linha-tabuleiro";
    faixa.setAttribute("role", "row");
    faixa.append(criarCelula(linha.id, "celula-cabecalho", "rowheader", linha.palavra));
    tabuleiro.colunas.forEach((coluna) => {
      const coordenada = `${linha.id}${coluna.id}`;
      const acerto = celulas.get(coordenada)?.estado === "acerto";
      const classe = acerto ? `celula-acerto${anteriores.has(coordenada) ? "" : " novo-acerto"}` : "celula-vazia";
      const celula = criarCelula(coordenada, classe, acerto ? "cell" : "button", acerto ? "✓ acerto" : "", acerto ? "div" : "button");
      celula.dataset.coordenada = coordenada;
      celula.setAttribute("aria-label", `${acerto ? "Carta posicionada em" : "Selecionar coordenada"} ${coordenada}: ${linha.palavra} e ${coluna.palavra}`);
      if (acerto) {
        faixa.append(celula);
      } else {
        // O botão nativo responde a Enter/Espaço. O contêiner mantém a semântica da tabela.
        celula.type = "button";
        celula.setAttribute("aria-pressed", "false");
        const espaco = document.createElement("div");
        espaco.className = "espaco-celula";
        espaco.setAttribute("role", "cell");
        espaco.append(celula);
        faixa.append(espaco);
      }
    });
    fragmento.append(faixa);
  });
  grade.replaceChildren(fragmento);
  atualizarSelecao();
}

function obterCelulaSelecionada() {
  return elemento("tabuleiro").querySelector("button[data-coordenada].celula-selecionada");
}

function atualizarSelecao() {
  const podeSelecionar = !ocupado && partida?.fase === "palpite";
  elemento("tabuleiro").querySelectorAll("button[data-coordenada]").forEach((celula) => {
    celula.disabled = !podeSelecionar;
  });
  const selecionada = obterCelulaSelecionada();
  elemento("confirmar-palpite").disabled = !podeSelecionar || !selecionada;
  elemento("selecao-palpite").textContent = selecionada
    ? `Coordenada selecionada: ${selecionada.dataset.coordenada}.`
    : "Nenhuma coordenada selecionada.";
}

function selecionarCelula(coordenada) {
  if (ocupado || partida?.fase !== "palpite") return;
  const celulas = [...elemento("tabuleiro").querySelectorAll("button[data-coordenada]")];
  const alvo = celulas.find((celula) => celula.dataset.coordenada === coordenada);
  if (!alvo || alvo.disabled) return;
  const selecionar = !alvo.classList.contains("celula-selecionada");
  // Uma única seleção; repetir o clique na mesma coordenada limpa o palpite.
  celulas.forEach((celula) => {
    const marcada = celula === alvo && selecionar;
    celula.classList.toggle("celula-selecionada", marcada);
    celula.setAttribute("aria-pressed", String(marcada));
  });
  atualizarSelecao();
}

function renderizarPlacar(placar) {
  validarPlacar(placar);
  elemento("acertos").textContent = elemento("acertos-finais").textContent = placar.acertos;
  elemento("erros").textContent = elemento("erros-finais").textContent = placar.erros;
}

function ocultarCarta() {
  elemento("carta-secreta").hidden = true;
  elemento("carta-secreta").textContent = "";
  elemento("revelar-carta").textContent = "Ver minha carta";
  elemento("revelar-carta").setAttribute("aria-expanded", "false");
}

function renderizarPartida(dados) {
  validarEstado(dados);
  const anteriores = new Set(partida?.tabuleiro.celulas.filter((celula) => celula.estado === "acerto").map((celula) => celula.coordenada));
  partida = dados;
  ocultarCarta();
  renderizarPlacar(dados.placar);
  renderizarTabuleiro(dados.tabuleiro, anteriores);
  elemento("form-dica").hidden = dados.fase !== "dica";
  elemento("form-palpite").hidden = dados.fase !== "palpite";
  elemento("turno").textContent = `Jogador ${dados.jogador_dica} dá a dica · Os demais adivinham juntos.`;
  elemento("mensagem-rodada").textContent = dados.mensagem || "";
  elemento("dica-atual").textContent = dados.dica || "";
  elemento("resumo-final").textContent = dados.resumo || "Obrigado por jogar em equipe!";
  elemento("form-dica").reset();
  elemento("form-palpite").reset();
  mostrarTela(dados.fase === "final" ? "tela-final" : "tela-jogo");
}

function abrirTelaDeNomes(evento) {
  evento.preventDefault();
  if (ocupado || !elemento("form-iniciar").reportValidity()) return;
  renderizarCamposDeNomes(Number(elemento("jogadores").value));
  elemento("erro").hidden = true;
  mostrarTela("tela-nomes-jogadores");
  focarTela();
}

function voltarParaInicio() {
  if (ocupado) return;
  elemento("erro").hidden = true;
  mostrarTela("tela-inicial");
  elemento("jogadores").focus();
}

async function confirmarNomes(evento) {
  evento.preventDefault();
  // O bloqueio é validado também no submit, inclusive para envio pelo teclado.
  if (ocupado || !validarNomes(true)) return;
  const nomes = obterCamposDeNomes().map((campo) => campo.value.trim());
  await iniciarPartida(nomes);
}

async function iniciarPartida(nomes) {
  await executarAcao(async () => {
    const configuracao = { jogadores: nomes.length, nomes };
    // Ponto de integração futura dos nomes: envie configuracao quando a API aceitar
    // esse campo. Por enquanto, registra os dados e mantém o fluxo de jogo existente.
    console.log("Jogadores da partida:", configuracao);
    const dados = await chamarAPI("/partida", "POST", { jogadores: configuracao.jogadores });
    renderizarPartida(dados);
  });
}

async function enviarDica(evento) {
  evento.preventDefault();
  await executarAcao(async () => {
    const dados = await chamarAPI(`/partida/${encodeURIComponent(partida.id)}/dica`, "POST", { dica: elemento("dica").value.trim() });
    renderizarPartida(dados);
  });
}

async function enviarPalpite(evento) {
  evento.preventDefault();
  const selecionada = obterCelulaSelecionada();
  if (ocupado || partida?.fase !== "palpite" || !selecionada || selecionada.disabled) return;
  // A coordenada vem da célula marcada, mantendo o contrato de envio à API.
  const coordenada = selecionada.dataset.coordenada;
  await executarAcao(async () => {
    const dados = await chamarAPI(`/partida/${encodeURIComponent(partida.id)}/palpite`, "POST", { palpite: coordenada });
    renderizarPartida(dados);
  });
}

async function atualizarPlacar() {
  await executarAcao(async () => {
    const placar = await chamarAPI(`/partida/${encodeURIComponent(partida.id)}/placar`);
    renderizarPlacar(placar);
    partida.placar = placar;
  });
}

function revelarCarta() {
  if (!elemento("carta-secreta").hidden) return ocultarCarta();
  elemento("carta-secreta").textContent = `Sua coordenada: ${partida.carta_secreta}`;
  elemento("carta-secreta").hidden = false;
  elemento("revelar-carta").textContent = "Esconder minha carta";
  elemento("revelar-carta").setAttribute("aria-expanded", "true");
}

function jogarNovamente() {
  partida = null;
  ocultarCarta();
  elemento("erro").hidden = true;
  mostrarTela("tela-inicial");
  focarTela();
}

elemento("form-iniciar").addEventListener("submit", abrirTelaDeNomes);
elemento("form-nomes").addEventListener("submit", confirmarNomes);
elemento("campos-nomes").addEventListener("input", () => validarNomes());
elemento("voltar-nomes").addEventListener("click", voltarParaInicio);
elemento("form-dica").addEventListener("submit", enviarDica);
elemento("form-palpite").addEventListener("submit", enviarPalpite);
// Delegação: um listener atende todas as células, inclusive após renderizar a rodada.
elemento("tabuleiro").addEventListener("click", (evento) => {
  const celula = evento.target.closest("button[data-coordenada]");
  if (celula && elemento("tabuleiro").contains(celula)) selecionarCelula(celula.dataset.coordenada);
});
elemento("revelar-carta").addEventListener("click", revelarCarta);
elemento("atualizar-placar").addEventListener("click", atualizarPlacar);
elemento("jogar-novamente").addEventListener("click", jogarNovamente);
