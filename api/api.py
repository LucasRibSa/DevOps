from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# ---------------------------
# CONFIGURAÇÃO DO BANCO
# ---------------------------

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "apidb")

def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

# ---------------------------
# CRIA TABELA SE NÃO EXISTIR
# ---------------------------

def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

inicializar_banco()

# ---------------------------
# ROTAS DA API
# ---------------------------

@app.route("/")
def home():
    return jsonify({"mensagem": "API Flask com PostgreSQL funcionando!"})

# LISTAR USUÁRIOS
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios ORDER BY id ASC;")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()

    lista = [
        {"id": u[0], "nome": u[1], "email": u[2]}
        for u in usuarios
    ]

    return jsonify(lista)

# CADASTRAR USUÁRIO
@app.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    dados = request.get_json()
    nome = dados.get("nome")
    email = dados.get("email")

    if not nome or not email:
        return jsonify({"erro": "Nome e e-mail são obrigatórios"}), 400

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, email) VALUES (%s, %s) RETURNING id;",
            (nome, email)
        )
        novo_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Usuário cadastrado", "id": novo_id}), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"erro": "E-mail já cadastrado"}), 400

# DELETAR USUÁRIO
@app.route("/usuarios/<int:id>", methods=["DELETE"])
def deletar_usuario(id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s RETURNING id;", (id,))
    apagado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if apagado:
        return jsonify({"mensagem": "Usuário deletado"})
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404


# ---------------------------
# EXECUTAR
# ---------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
