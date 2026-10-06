"""Regras e representação da partida consumida pela interface web."""

from src.Baralho import Baralho


LINHAS = (
    {"id": "A", "palavra": "mar"},
    {"id": "B", "palavra": "casa"},
    {"id": "C", "palavra": "música"},
)
COLUNAS = (
    {"id": "1", "palavra": "noite"},
    {"id": "2", "palavra": "festa"},
    {"id": "3", "palavra": "viagem"},
)


def criar_cartas():
    baralho = Baralho([linha["id"] for linha in LINHAS], [coluna["id"] for coluna in COLUNAS])
    baralho.embaralhar()
    return baralho.cartas


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
        "jogador_dica": indice % partida["num_jogadores"] + 1,
        "carta_secreta": cartas[indice] if fase == "dica" else None,
        "dica": progresso["dica"] if fase == "palpite" else None,
        "tabuleiro": {
            "linhas": list(LINHAS),
            "colunas": list(COLUNAS),
            "celulas": [
                {"coordenada": carta, "estado": "acerto" if carta in acertos else "vazia"}
                for carta in [f"{linha['id']}{coluna['id']}" for linha in LINHAS for coluna in COLUNAS]
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
