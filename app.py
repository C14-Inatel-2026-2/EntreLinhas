from flask import Flask, request, jsonify
from db import conectar_bd, criar_tabelas, criar_partida, consultar_partida, salvar_jogada

app = Flask(__name__)

# garante que as tabelas existem quando a api sobe
with app.app_context():
    conn = conectar_bd()
    criar_tabelas(conn)
    conn.close()

@app.route("/partida", methods=["POST"])
def rota_criar_partida():
    data = request.get_json() or {}
    num_jogadores = data.get("num_jogadores")
    
    if not num_jogadores or not isinstance(num_jogadores, int) or num_jogadores <= 0:
        return jsonify({"erro": "Número de jogadores inválido"}), 400

    conn = conectar_bd()
    partida_id = criar_partida(conn, num_jogadores)
    conn.close()

    return jsonify({
        "mensagem": "Partida criada com sucesso",
        "partida_id": partida_id,
        "num_jogadores": num_jogadores
    }), 201

@app.route("/partida/<int:partida_id>", methods=["GET"])
def rota_obter_placar(partida_id):
    conn = conectar_bd()
    partida = consultar_partida(conn, partida_id)
    conn.close()

    if not partida:
        return jsonify({"erro": "Partida não encontrada"}), 404

    return jsonify(partida), 200

@app.route("/partida/<int:partida_id>/palpite", methods=["POST"])
def rota_palpite(partida_id):
    conn = conectar_bd()
    partida = consultar_partida(conn, partida_id)
    
    if not partida:
        conn.close()
        return jsonify({"erro": "Partida não encontrada"}), 404

    data = request.get_json() or {}
    jogador = data.get("jogador")
    dica = data.get("dica")
    coord_correta = data.get("coordenada_correta")
    coord_tentada = data.get("coordenada_tentada")
    ordem = data.get("ordem", 1)

    if not all([jogador, dica, coord_correta, coord_tentada]):
        conn.close()
        return jsonify({"erro": "Dados da jogada incompletos"}), 400

    jogada_id = salvar_jogada(conn, partida_id, jogador, dica, coord_correta, coord_tentada, ordem)
    acertou = (coord_correta == coord_tentada)
    conn.close()

    return jsonify({
        "jogada_id": jogada_id,
        "acertou": acertou,
        "mensagem": "Palpite correto!" if acertou else "Palpite incorreto!"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)