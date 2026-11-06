"""Regras e representação da partida consumida pela interface web."""

from datetime import datetime
from src.Baralho import Baralho


LINHAS = ("A", "B", "C")
COLUNAS = ("1", "2", "3")

REFERENCIA_EXPRESSO_SEGUNDOS = 5 * 60

def criar_cartas():
    baralho = Baralho(LINHAS, COLUNAS)
    baralho.embaralhar()
    return baralho.cartas


def jogador_da_rodada(partida, progresso):
    ordem = progresso.get("ordem_jogadores")
    if ordem:
        return ordem[min(progresso["indice"], len(ordem) - 1)]
    return progresso["indice"] % partida["num_jogadores"] + 1

def duracao_segundos(partida):
    if not partida.get("data_inicio"):
        return None
    inicio = datetime.fromisoformat(partida["data_inicio"])
    fim = datetime.fromisoformat(partida["data_fim"]) if partida.get("data_fim") else datetime.now()
    return max(0, int((fim - inicio).total_seconds()))

def avaliar_desempenho(acertos, jogadas, total_cartas, duracao):
    """Faixas oficiais do Expresso; tempo é referência, sem penalidade."""
    if acertos < 4:
        classificacao = "Fracasso"
    elif acertos < 6:
        classificacao = "Mediano"
    elif acertos < 8:
        classificacao = "Bom"
    else:
        classificacao = "Espetacular"
    dentro_referencia = None if duracao is None else duracao <= REFERENCIA_EXPRESSO_SEGUNDOS
    return {
        "classificacao": classificacao,
        "concluida": jogadas == total_cartas,
        "cartas_restantes": total_cartas - jogadas,
        "total_cartas": total_cartas,
        "referencia_segundos": REFERENCIA_EXPRESSO_SEGUNDOS,
        "dentro_referencia": dentro_referencia,
    }


def montar_estado(partida, progresso, jogadas, mensagem=None):
    acertos = {jogada["coordenada_correta"] for jogada in jogadas if jogada["acertou"]}
    placar = {"acertos": len(acertos), "erros": len(jogadas) - len(acertos)}
    cartas = progresso["cartas"]
    indice = progresso["indice"]
    fase = progresso["fase"]
    duracao = duracao_segundos(partida)

    estado = {
        "id": partida["id"],
        "partida_id": partida["id"],
        "num_jogadores": partida["num_jogadores"],
        "fase": fase,
        "jogador_dica": jogador_da_rodada(partida, progresso),
        "carta_secreta": cartas[indice] if fase == "dica" else None,
        "dica": progresso["dica"] if fase == "palpite" else None,
        "tabuleiro": {
            "linhas": [{"id": id_, "palavra": palavra} for id_, palavra in zip(LINHAS, progresso["palavras"][:3])],
            "colunas": [{"id": id_, "palavra": palavra} for id_, palavra in zip(COLUNAS, progresso["palavras"][3:])],
            "celulas": [
                {"coordenada": carta, "estado": "acerto" if carta in acertos else "vazia"}
                for carta in [f"{linha}{coluna}" for linha in LINHAS for coluna in COLUNAS]
            ],
        },
        "placar": placar,
        "turno": progresso["indice"],
        "duracao_segundos": duracao,
    }
    if mensagem:
        estado["mensagem"] = mensagem
    if fase == "final":
        estado["desempenho"] = avaliar_desempenho(placar["acertos"], len(jogadas), len(cartas), duracao)
        estado["resumo"] = (
            f"Partida encerrada: {placar['acertos']} cartas posicionadas "
            f"e {placar['erros']} descartadas."
        )
    return estado
