"""Regras e representação da partida consumida pela interface web."""

import math
import time
from datetime import datetime
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

TEMPO_PALPITE = 120
TAMANHO_MAXIMO_DICA = 60


def dica_valida(dica):
    """A dica é uma única palavra, com até 60 caracteres sem os espaços das pontas."""
    return (
        isinstance(dica, str)
        and len(dica.split()) == 1
        and len(dica.strip()) <= TAMANHO_MAXIMO_DICA
    )


def proxima_rodada(progresso):
    """Índice e fase depois que a carta atual é jogada ou descartada.

    A partida volta para a fase de dica até a última carta; depois dela, fase final.
    """
    novo_indice = progresso["indice"] + 1
    fase = "final" if novo_indice == len(progresso["cartas"]) else "dica"
    return novo_indice, fase


def segundos_restantes(progresso):
    inicio = progresso.get("turno_inicio")
    if progresso["fase"] != "palpite" or inicio is None:
        return None
    return TEMPO_PALPITE - (time.time() - inicio)


def tempo_esgotado(progresso):
    restante = segundos_restantes(progresso)
    return restante is not None and restante <= 0


def duracao_segundos(partida):
    if not partida.get("data_inicio"):
        return None
    inicio = datetime.fromisoformat(partida["data_inicio"])
    fim = datetime.fromisoformat(partida["data_fim"]) if partida.get("data_fim") else datetime.now()
    return max(0, int((fim - inicio).total_seconds()))

def avaliar_desempenho(acertos, jogadas, total_cartas):
    """Faixas oficiais do Expresso, determinadas apenas pelos acertos."""
    if acertos < 4:
        classificacao = "Fracasso"
    elif acertos < 6:
        classificacao = "Mediano"
    elif acertos < 8:
        classificacao = "Bom"
    else:
        classificacao = "Espetacular"
    return {
        "classificacao": classificacao,
        "concluida": jogadas == total_cartas,
        "cartas_restantes": total_cartas - jogadas,
        "total_cartas": total_cartas,
    }


def coordenadas_acertadas(jogadas):
    """Coordenadas já posicionadas no tabuleiro."""
    return {jogada["coordenada_correta"] for jogada in jogadas if jogada["acertou"]}


def calcular_placar(jogadas):
    """Acertos e erros da partida; os acertos também são a pontuação final.

    Cada carta sai uma única vez e uma coordenada preenchida não aceita novo
    palpite, então contar coordenadas distintas equivale a somar os acertos.
    """
    acertos = len(coordenadas_acertadas(jogadas))
    return {"acertos": acertos, "erros": len(jogadas) - acertos}


def montar_tabuleiro(palavras, acertos):
    """Grade 3 × 3: três palavras nas linhas, três nas colunas e o estado das nove células."""
    return {
        "linhas": [{"id": id_, "palavra": palavra} for id_, palavra in zip(LINHAS, palavras[:3])],
        "colunas": [{"id": id_, "palavra": palavra} for id_, palavra in zip(COLUNAS, palavras[3:])],
        "celulas": [
            {"coordenada": carta, "estado": "acerto" if carta in acertos else "vazia"}
            for carta in [f"{linha}{coluna}" for linha in LINHAS for coluna in COLUNAS]
        ],
    }


def montar_estado(partida, progresso, jogadas, mensagem=None):
    acertos = coordenadas_acertadas(jogadas)
    placar = calcular_placar(jogadas)
    cartas = progresso["cartas"]
    indice = progresso["indice"]
    fase = progresso["fase"]
    duracao = duracao_segundos(partida)
    restante = segundos_restantes(progresso)

    estado = {
        "id": partida["id"],
        "partida_id": partida["id"],
        "num_jogadores": partida["num_jogadores"],
        "fase": fase,
        "jogador_dica": jogador_da_rodada(partida, progresso),
        "carta_secreta": cartas[indice] if fase == "dica" else None,
        "dica": progresso["dica"] if fase == "palpite" else None,
        "tabuleiro": montar_tabuleiro(progresso["palavras"], acertos),
        "placar": placar,
        "turno": progresso["indice"],
        "duracao_segundos": duracao,
        "tempo_restante": None if restante is None else max(0, math.ceil(restante)),
    }
    if mensagem:
        estado["mensagem"] = mensagem
    if fase == "final":
        estado["desempenho"] = avaliar_desempenho(placar["acertos"], len(jogadas), len(cartas))
        estado["resumo"] = (
            f"Partida encerrada: {placar['acertos']} cartas posicionadas "
            f"e {placar['erros']} descartadas."
        )
    return estado
