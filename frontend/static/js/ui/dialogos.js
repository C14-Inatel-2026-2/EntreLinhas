/* Apresentação e ciclo de vida dos diálogos; o estado da partida fica na SPA. */
import { elemento } from "../utils/dom.js";

export function focarDialogoAberto() {
  if (elemento("inicio-turno").open) {
    elemento("continuar-turno").focus();
    return true;
  }
  if (elemento("resultado-palpite").open) {
    elemento("continuar-palpite").focus();
    return true;
  }
  return false;
}

export function mostrarInicioTurno(nome, fase) {
  elemento("nome-inicio-turno").textContent = nome;
  elemento("descricao-inicio-turno").textContent = fase === "palpite"
    ? "Você dá o primeiro palpite com a ajuda do time."
    : "Você começa dando a dica. Só você pode ver a carta secreta!";
  elemento("inicio-turno").showModal();
}

export function mostrarResultadoPalpite(acertou, fase) {
  const popup = elemento("resultado-palpite");
  popup.dataset.resultado = acertou ? "acerto" : "erro";
  elemento("icone-palpite").textContent = acertou ? "✓" : "×";
  elemento("titulo-palpite").textContent = acertou ? "Acertou!" : "Errou!";
  elemento("descricao-palpite").textContent = acertou
    ? "Boa conexão! Mais uma carta posicionada no tabuleiro."
    : "Essa não era a coordenada. A carta foi descartada, mas cada ideia conta!";
  elemento("continuar-palpite").textContent = fase === "final" ? "Ver resultado" : "Continuar";
  popup.showModal();
}

export function mostrarTempoEsgotado(fase) {
  const popup = elemento("resultado-palpite");
  popup.dataset.resultado = "erro";
  elemento("icone-palpite").textContent = "⏱";
  elemento("titulo-palpite").textContent = "Tempo esgotado!";
  elemento("descricao-palpite").textContent = "A carta foi descartada e um erro foi adicionado ao placar.";
  elemento("continuar-palpite").textContent = fase === "final" ? "Ver resultado" : "Continuar";
  popup.showModal();
}

export function configurarDialogos(focarTela) {
  elemento("continuar-palpite").addEventListener("click", () => elemento("resultado-palpite").close());
  elemento("continuar-turno").addEventListener("click", () => elemento("inicio-turno").close());
  elemento("inicio-turno").addEventListener("close", focarTela);
  elemento("resultado-palpite").addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") {
      evento.preventDefault();
      elemento("resultado-palpite").close();
    }
  });
  elemento("resultado-palpite").addEventListener("close", focarTela);
}
