/* Cliente HTTP: serialização JSON, timeout e mensagens de erro da API. */
import { USAR_MOCK, API_BASE } from "../config.js";
import { requisitarMock } from "../mocks/partida.js";

export async function chamarAPI(caminho, metodo = "GET", corpo) {
  // Troque USAR_MOCK em js/config.js: as chamadas reais já estão implementadas abaixo.
  if (USAR_MOCK) return requisitarMock(caminho, metodo);
  const controlador = new AbortController();
  const timeout = setTimeout(() => controlador.abort(), 15000);
  try {
    const resposta = await fetch(`${API_BASE}${caminho}`, {
      method: metodo,
      headers: corpo ? { Accept: "application/json", "Content-Type": "application/json" } : { Accept: "application/json" },
      body: corpo ? JSON.stringify(corpo) : undefined,
      signal: controlador.signal
    });
    const dados = await resposta.json().catch(() => null);
    if (!resposta.ok) throw new Error(dados?.erro || `Não foi possível concluir a ação (HTTP ${resposta.status}).`);
    if (!dados) throw new Error("A API não retornou um JSON válido.");
    return dados;
  } catch (erro) {
    if (erro.name === "AbortError") throw new Error("O servidor demorou a responder. A ação pode ter sido recebida; verifique a conexão antes de tentar novamente.");
    if (erro instanceof TypeError) throw new Error("Não foi possível conectar ao servidor. Verifique a conexão e o endereço da API.");
    throw erro;
  } finally {
    clearTimeout(timeout);
  }
}

