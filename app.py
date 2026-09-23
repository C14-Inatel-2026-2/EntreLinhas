from flask import Flask, request, jsonify
from db import (
    conectar_bd, criar_tabelas, criar_partida, consultar_partida, salvar_jogada,
    criar_estado, consultar_estado, atualizar_estado, consultar_jogadas, finalizar_partida,
)
from jogo import criar_cartas, montar_estado

app = Flask(__name__)

# garante que as tabelas existem quando a api sobe
with app.app_context():
    conn = conectar_bd()
    criar_tabelas(conn)
    conn.close()

@app.route("/partida", methods=["POST"])
def rota_criar_partida():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"erro": "Número de jogadores inválido"}), 400
    num_jogadores = data.get("num_jogadores")

    if type(num_jogadores) is not int or not 2 <= num_jogadores <= 6:
        return jsonify({"erro": "Número de jogadores inválido"}), 400

    conn = conectar_bd()
    try:
        partida_id = criar_partida(conn, num_jogadores)
        criar_estado(conn, partida_id, criar_cartas())
        partida = consultar_partida(conn, partida_id)
        progresso = consultar_estado(conn, partida_id)
        return jsonify(montar_estado(partida, progresso, [])), 201
    finally:
        conn.close()

@app.route("/partida/<int:partida_id>", methods=["GET"])
def rota_obter_placar(partida_id):
    conn = conectar_bd()
    partida = consultar_partida(conn, partida_id)
    conn.close()

    if not partida:
        return jsonify({"erro": "Partida não encontrada"}), 404

    return jsonify(partida), 200


@app.route("/partida/<int:partida_id>/placar", methods=["GET"])
def rota_placar(partida_id):
    conn = conectar_bd()
    try:
        if not consultar_estado(conn, partida_id):
            return jsonify({"erro": "Partida não encontrada"}), 404
        jogadas = consultar_jogadas(conn, partida_id)
        acertos = sum(jogada["acertou"] for jogada in jogadas)
        return jsonify({"acertos": acertos, "erros": len(jogadas) - acertos}), 200
    finally:
        conn.close()


@app.route("/partida/<int:partida_id>/dica", methods=["POST"])
def rota_dica(partida_id):
    conn = conectar_bd()
    try:
        partida = consultar_partida(conn, partida_id)
        progresso = consultar_estado(conn, partida_id)
        if not partida or not progresso:
            return jsonify({"erro": "Partida não encontrada"}), 404
        if progresso["fase"] != "dica":
            return jsonify({"erro": "Não é a vez de enviar uma dica"}), 409

        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"erro": "A dica deve ter uma única palavra de até 60 caracteres"}), 400
        dica = data.get("dica")
        if not isinstance(dica, str) or not dica.strip() or len(dica.strip()) > 60 or len(dica.split()) != 1:
            return jsonify({"erro": "A dica deve ter uma única palavra de até 60 caracteres"}), 400

        atualizar_estado(conn, partida_id, progresso["indice"], "palpite", dica.strip())
        progresso = consultar_estado(conn, partida_id)
        return jsonify(montar_estado(partida, progresso, consultar_jogadas(conn, partida_id))), 200
    finally:
        conn.close()

@app.route("/partida/<int:partida_id>/palpite", methods=["POST"])
def rota_palpite(partida_id):
    conn = conectar_bd()
    try:
        partida = consultar_partida(conn, partida_id)
        progresso = consultar_estado(conn, partida_id)
        if not partida or not progresso:
            return jsonify({"erro": "Partida não encontrada"}), 404

        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"erro": "Coordenada inválida"}), 400
        palpite = data.get("palpite")
        if progresso["fase"] != "palpite":
            return jsonify({"erro": "Não é a vez de enviar um palpite"}), 409
        if not isinstance(palpite, str) or palpite not in progresso["cartas"]:
            return jsonify({"erro": "Coordenada inválida"}), 400

        jogadas = consultar_jogadas(conn, partida_id)
        acertos = {jogada["coordenada_correta"] for jogada in jogadas if jogada["acertou"]}
        if palpite in acertos:
            return jsonify({"erro": "Essa coordenada já foi preenchida"}), 400

        correta = progresso["cartas"][progresso["indice"]]
        acertou = palpite == correta
        jogador = str(progresso["indice"] % partida["num_jogadores"] + 1)
        salvar_jogada(conn, partida_id, jogador, progresso["dica"], correta, palpite, progresso["indice"] + 1)
        novo_indice = progresso["indice"] + 1
        fase = "final" if novo_indice == len(progresso["cartas"]) else "dica"
        atualizar_estado(conn, partida_id, novo_indice, fase)
        if fase == "final":
            pontuacao = sum(jogada["acertou"] for jogada in consultar_jogadas(conn, partida_id))
            finalizar_partida(conn, partida_id, pontuacao)
        progresso = consultar_estado(conn, partida_id)
        mensagem = "Palpite correto!" if acertou else "Palpite incorreto!"
        return jsonify(montar_estado(partida, progresso, consultar_jogadas(conn, partida_id), mensagem)), 200
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
