import os
from engine.auto_fetcher import AutoFetcher
from engine.exporter import Exporter


def run_cycle(aporte_total=0, modo="moderado"):
    """
    Executa o ciclo completo:
    - Busca dados da carteira
    - Atualiza preços e fundamentos via BRAPI
    - Calcula valuation simples
    - Calcula score
    - Gera dashboard HTML
    - Retorna dados para o Flask
    """

    # ============================================================
    # 1. Buscar dados da carteira + dados de mercado
    # ============================================================
    dados = AutoFetcher.atualizar_dados()

    if not dados:
        print("⚠️ Nenhum dado retornado pela atualização.")
        return {"acoes": [], "fiis": [], "riscos": []}

    acoes = []
    fiis = []

    # ============================================================
    # 2. Processar cada ativo
    # ============================================================
    for ticker, info in dados.items():

        preco = info["preco"]
        dy = info["dy"]
        pvp = info["pvp"]
        lpa = info["lpa"]
        vpa = info["vpa"]
        roe = info["roe"]
        cagr = info["cagr"]
        quant = info["quant"]
        tipo = info["tipo"]

        # ============================================================
        # 3. Valuation simples
        # ============================================================
        valor_justo = 0
        margem = 0

        if lpa and vpa:
            valor_justo = round((lpa * 12 + vpa) / 2, 2)

        if preco > 0 and valor_justo > 0:
            margem = round(((valor_justo - preco) / preco) * 100, 2)

        # ============================================================
        # 4. Score simples
        # ============================================================
        score = 0
        if dy > 3: score += 1
        if pvp < 1.5: score += 1
        if roe > 10: score += 1
        if cagr > 5: score += 1
        if margem > 0: score += 1

        ativo = {
            "ticker": ticker,
            "quant": quant,
            "preco": preco,
            "dy": dy,
            "pvp": pvp,
            "lpa": lpa,
            "vpa": vpa,
            "roe": roe,
            "cagr": cagr,
            "valor_justo": valor_justo,
            "margem": margem,
            "score": score,
        }

        if tipo == "acao":
            acoes.append(ativo)
        else:
            fiis.append(ativo)

    # ============================================================
    # 5. Gerar HTML do dashboard
    # ============================================================
    html = gerar_html_dashboard(acoes, fiis, aporte_total)
    Exporter.gerar_dashboard(html)

    # ============================================================
    # 6. Retornar dados para o Flask
    # ============================================================
    return {
        "acoes": acoes,
        "fiis": fiis,
        "riscos": []  # risco desativado por enquanto
    }


# ============================================================
# GERAÇÃO DO HTML DO DASHBOARD
# ============================================================
def gerar_html_dashboard(acoes, fiis, aporte_total):
    html = """
    <h1>📈 Matrix Invest Analyzer PRO</h1>
    <h2>💼 Ações</h2>
    <table>
        <tr>
            <th>Ticker</th><th>Preço</th><th>DY</th><th>P/VP</th>
            <th>LPA</th><th>VPA</th><th>ROE</th><th>CAGR</th>
            <th>V. Justo</th><th>Margem</th><th>Score</th>
        </tr>
    """

    for a in acoes:
        html += f"""
        <tr>
            <td>{a['ticker']}</td>
            <td>R$ {a['preco']}</td>
            <td>{a['dy']}%</td>
            <td>{a['pvp']}</td>
            <td>{a['lpa']}</td>
            <td>{a['vpa']}</td>
            <td>{a['roe']}%</td>
            <td>{a['cagr']}%</td>
            <td>R$ {a['valor_justo']}</td>
            <td>{a['margem']}%</td>
            <td>{a['score']}</td>
        </tr>
        """

    html += "</table>"

    html += """
    <h2>🏢 Fundos Imobiliários</h2>
    <table>
        <tr>
            <th>Ticker</th><th>Preço</th><th>DY</th><th>P/VP</th>
            <th>VPA</th><th>Score</th>
        </tr>
    """

    for f in fiis:
        html += f"""
        <tr>
            <td>{f['ticker']}</td>
            <td>R$ {f['preco']}</td>
            <td>{f['dy']}%</td>
            <td>{f['pvp']}</td>
            <td>{f['vpa']}</td>
            <td>{f['score']}</td>
        </tr>
        """

    html += "</table>"

    return html
