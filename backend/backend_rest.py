# backend.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

def conectar_db():
    return sqlite3.connect('aposta.db')

def serialize_jogos_futuros(rows):
    keys = ["id", "liga", "data", "time_casa", "time_fora", "odds", "palpite", "confianca"]
    return [dict(zip(keys, row)) for row in rows]

def serialize_jogos_historicos(rows):
    keys = ["id", "liga", "data", "time_casa", "time_fora", "placar_casa", "placar_fora", "estatisticas"]
    return [dict(zip(keys, row)) for row in rows]

@app.route('/api/jogos', methods=['GET'])
def jogos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jogos_futuros ORDER BY data")
        jogos = cursor.fetchall()
        conn.close()
        return jsonify(serialize_jogos_futuros(jogos))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jogos/historicos', methods=['GET'])
def historicos():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jogos_historicos ORDER BY data DESC LIMIT 20")
        historicos = cursor.fetchall()
        conn.close()
        return jsonify(serialize_jogos_historicos(historicos))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/palpites', methods=['POST'])
def palpites():
    data = request.json
    required_fields = ["usuario", "jogo_id", "mercado", "palpite", "probabilidade"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {field}"}), 400
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO palpites (usuario, jogo_id, mercado, palpite, probabilidade)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['usuario'],
            data['jogo_id'],
            data['mercado'],
            data['palpite'],
            data['probabilidade']
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "palpite registrado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)