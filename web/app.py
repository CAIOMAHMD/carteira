from flask import Flask, render_template, send_file, redirect, request, url_for
import os
import sqlite3

from engine.run_cycle import run_cycle
from engine.auto_fetcher import AutoFetcher

# ============================
# CONFIGURAÇÃO DO FLASK
# ============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Caminho do banco (correto para rodar dentro da pasta /web)
DB_PATH = "/app/web/carteira.db"



# ============================
# ROTAS
# ============================

@app.route("/")
def index():
    # 1) Carteira REAL (banco)
    carteira = AutoFetcher._get_carteira()

    # 2) Dados de mercado
    resultado = run_cycle(aporte_total=0, modo="moderado")

    return render_template("index.html", carteira=carteira, resultado=resultado)


@app.route("/dashboard")
def dashboard():
    dashboard_path = os.path.abspath(os.path.join(BASE_DIR, "..", "exports", "dashboard.html"))

    if not os.path.exists(dashboard_path):
        return "Dashboard ainda não foi gerado. Rode o ciclo primeiro."

    return send_file(dashboard_path)


@app.route("/run")
def run():
    aporte = request.args.get("aporte", 500, type=int)
    modo = request.args.get("modo", "moderado")

    resultado = run_cycle(aporte_total=aporte, modo=modo)

    return render_template("carteira.html", resultado=resultado)


@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        aporte = request.form.get("aporte")
        modo = request.form.get("modo")
        return redirect(url_for("run", aporte=aporte, modo=modo))

    return render_template("config.html")


@app.route("/login")
def login():
    return render_template("login.html")


# ============================
# ADICIONAR ATIVO
# ============================

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        ticker = request.form["ticker"].upper().strip()
        quant = int(request.form["quant"])
        tipo = request.form["tipo"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Verifica duplicado
        c.execute("SELECT 1 FROM carteira WHERE ticker = ?", (ticker,))
        existe = c.fetchone()

        if existe:
            conn.close()
            return "Ativo já existe na carteira."

        c.execute(
            "INSERT INTO carteira (ticker, quantidade, tipo) VALUES (?, ?, ?)",
            (ticker, quant, tipo)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")


# ============================
# REMOVER ATIVO
# ============================

@app.route("/delete/<ticker>")
def delete(ticker):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM carteira WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False)
