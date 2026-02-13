import os
import pandas as pd
from datetime import datetime

HIST_PATH = "data/historico.csv"
OUT_PATH = "webapp/static/dashboard.html"

def gerar_dashboard():
    if not os.path.exists(HIST_PATH):
        print("⚠️ Sem histórico para gerar dashboard.")
        return

    df = pd.read_csv(HIST_PATH, sep=";")

    # pega só o último dia
    ultima_data = df["data"].max()
    hoje = df[df["data"] == ultima_data].copy()

    # ordena por score e margem
    rank_compra = hoje.sort_values(["status", "score", "margem"], ascending=[True, False, False])

    html_tabela = rank_compra[[
        "ticker", "price", "valor_justo", "margem", "score", "status", "dy", "pvp", "is_fii"
    ]].to_html(index=False, classes="tabela", float_format="%.2f")

    html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Dashboard Carteira</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #111; color: #eee; }}
            h1 {{ margin-bottom: 5px; }}
            .sub {{ color: #aaa; margin-bottom: 20px; }}
            table.tabela {{ border-collapse: collapse; width: 100%; }}
            table.tabela th, table.tabela td {{ border: 1px solid #444; padding: 6px 8px; text-align: right; }}
            table.tabela th {{ background: #222; }}
            table.tabela td:first-child, table.tabela th:first-child {{ text-align: left; }}
        </style>
    </head>
    <body>
        <h1>Dashboard da Carteira</h1>
        <div class="sub">Atualizado em {ultima_data}</div>
        {html_tabela}
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"📊 Dashboard gerado em: {OUT_PATH}")
