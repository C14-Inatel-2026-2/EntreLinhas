/* Renderização e validação dos campos de nomes, independente da navegação. */
import { elemento } from "../utils/dom.js";

export function obterCamposDeNomes() {
  return [...elemento("campos-nomes").querySelectorAll("input")];
}

export function validarNomes(mostrarErro = false) {
  const campos = obterCamposDeNomes();
  const vazios = campos.filter((campo) => !campo.value.trim());
  const validos = campos.length >= 2 && campos.length <= 6 && vazios.length === 0;
  elemento("comecar-jogo").setAttribute("aria-disabled", String(!validos));
  const exibirErro = !validos && (mostrarErro || !elemento("erro-nomes").hidden);
  elemento("erro-nomes").hidden = !exibirErro;
  elemento("erro-nomes").textContent = exibirErro ? "Falta alguém! Preencha o nome de cada jogador para continuar." : "";
  campos.forEach((campo) => campo.setAttribute("aria-invalid", String(exibirErro && !campo.value.trim())));
  if (mostrarErro && !validos) vazios[0]?.focus();
  return validos;
}

export function renderizarCamposDeNomes(quantidade) {
  // Preserva os nomes já digitados ao voltar e ajustar o tamanho da turma.
  const nomesAnteriores = obterCamposDeNomes().map((campo) => campo.value);
  const fragmento = document.createDocumentFragment();
  for (let indice = 0; indice < quantidade; indice += 1) {
    const grupo = document.createElement("div");
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.id = `nome-jogador-${indice + 1}`;
    input.name = `nome-jogador-${indice + 1}`;
    input.type = "text";
    input.placeholder = "Digite o nome";
    input.required = true;
    input.value = nomesAnteriores[indice] || "";
    input.setAttribute("aria-describedby", "ajuda-nomes erro-nomes");
    label.htmlFor = input.id;
    label.textContent = `Jogador ${indice + 1}`;
    grupo.append(label, input);
    fragmento.append(grupo);
  }
  elemento("campos-nomes").replaceChildren(fragmento);
  elemento("erro-nomes").hidden = true;
  validarNomes();
}

