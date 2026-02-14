import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from engine.auto_fetcher import AutoFetcher

app = Flask(__name__)

DB_PATH = "/app/web/carteira.db"


# ============================================================
# FUNÇÕES DE BANCO
# ============================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================
# CÁLCULO DA POSIÇÃO REAL (USANDO MOVIMENTAÇÕES)
# ============================================================

def calcular_posicao(ticker):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT tipo, quantidade, preco
        FROM movimentacoes
        WHERE ticker = ?
    """, (ticker,))
    movs = c.fetchall()
    conn.close()

    if not movs:
        return None

    total_comprado = 0
    total_investido = 0
    total_vendido = 0

    for tipo, qtd, preco in movs:
        if tipo == "compra":
            total_comprado += qtd
            total_investido += qtd * preco
        elif tipo == "venda":
            total_vendido += qtd

    quantidade_atual = total_comprado - total_vendido

    if quantidade_atual <= 0:
        return None

    preco_medio = total_investido / total_comprado

    return {
        "quantidade": quantidade_atual,
        "preco_medio": preco_medio,
        "total_investido": preco_medio * quantidade_atual
    }


# ============================================================
# ROTAS
# ============================================================

@app.route("/")
def index():
    dados = AutoFetcher.atualizar_dados()

    # Enriquecer dados com posição real
    for lista in [dados["acoes"], dados["fiis"]]:
        for item in lista:
            pos = calcular_posicao(item["ticker"])
            if not pos:
                continue

            item["quantidade"] = pos["quantidade"]
            item["preco_medio"] = pos["preco_medio"]
            item["total_investido"] = pos["total_investido"]

            if item["preco"]:
                item["total_atual"] = item["preco"] * pos["quantidade"]
                item["lucro"] = item["total_atual"] - item["total_investido"]
                item["rentabilidade"] = item["lucro"] / item["total_investido"]

    return render_template("index.html", dados=dados)


@app.route("/comprar", methods=["GET", "POST"])
def comprar():
    if request.method == "POST":
        ticker = request.form["ticker"].upper().strip()
        quantidade = float(request.form["quantidade"])
        preco = float(request.form["preco"])

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO movimentacoes (ticker, tipo, quantidade, preco)
            VALUES (?, 'compra', ?, ?)
        """, (ticker, quantidade, preco))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("comprar.html")


@app.route("/vender", methods=["GET", "POST"])
def vender():
    if request.method == "POST":
        ticker = request.form["ticker"].upper().strip()
        quantidade = float(request.form["quantidade"])
        preco = float(request.form["preco"])

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO movimentacoes (ticker, tipo, quantidade, preco)
            VALUES (?, 'venda', ?, ?)
        """, (ticker, quantidade, preco))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("vender.html")


@app.route("/carteira")
def carteira():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT ticker FROM movimentacoes")
    tickers = [row[0] for row in c.fetchall()]
    conn.close()

    posicoes = []

    for t in tickers:
        pos = calcular_posicao(t)
        if pos:
            posicoes.append({"ticker": t, **pos})

    return render_template("carteira.html", posicoes=posicoes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
