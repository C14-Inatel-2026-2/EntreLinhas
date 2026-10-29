"""Regras e representação da partida consumida pela interface web."""

from src.Baralho import Baralho


LINHAS = ("A", "B", "C")
COLUNAS = ("1", "2", "3")

def criar_cartas():
    baralho = Baralho(LINHAS, COLUNAS)
    baralho.embaralhar()
    return baralho.cartas


def jogador_da_rodada(partida, progresso):
    ordem = progresso.get("ordem_jogadores")
    if ordem:
        return ordem[min(progresso["indice"], len(ordem) - 1)]
    return progresso["indice"] % partida["num_jogadores"] + 1


def montar_estado(partida, progresso, jogadas, mensagem=None):
    acertos = {jogada["coordenada_correta"] for jogada in jogadas if jogada["acertou"]}
    placar = {"acertos": len(acertos), "erros": len(jogadas) - len(acertos)}
    cartas = progresso["cartas"]
    indice = progresso["indice"]
    fase = progresso["fase"]

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
    }
    if mensagem:
        estado["mensagem"] = mensagem
    if fase == "final":
        estado["resumo"] = (
            f"Partida encerrada: {placar['acertos']} cartas posicionadas "
            f"e {placar['erros']} descartadas."
        )
    return estado
