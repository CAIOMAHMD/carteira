import os
import sqlite3
import requests
from dotenv import load_dotenv

# ============================
# CONFIGURAÇÃO
# ============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mesmo caminho que você colocou no app.py
DB_PATH = "/app/web/carteira.db"

# Carrega variáveis de ambiente (.env ou Docker ENV)
load_dotenv()

BRAPI_TOKEN = (
    os.getenv("BRAPI_TOKEN")
    or os.getenv("BRAPI_API_KEY")
)

if not BRAPI_TOKEN:
    raise RuntimeError("BRAPI_TOKEN / BRAPI_API_KEY não definido no ambiente.")


class AutoFetcher:
    @staticmethod
    def _get_carteira():
        """
        Lê a tabela carteira do banco e retorna uma lista de tuplas:
        [(ticker, quantidade, tipo), ...]
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT ticker, quantidade, tipo FROM carteira")
        rows = c.fetchall()
        conn.close()
        return rows

    @staticmethod
    def _fetch_brapi_data(tickers):
        """
        Busca dados na BRAPI para uma lista de tickers.
        Retorna um dicionário {ticker: dados}.
        """
        if not tickers:
            return {}

        base_url = "https://brapi.dev/api/quote"
        headers = {"User-Agent": "carteira-app"}

        result = {}

        for ticker in tickers:
            try:
                url = f"{base_url}/{ticker}?token={BRAPI_TOKEN}"
                resp = requests.get(url, headers=headers, timeout=10)

                if resp.status_code != 200:
                    continue

                data = resp.json()
                if "results" not in data or not data["results"]:
                    continue

                quote = data["results"][0]
                result[ticker] = quote

            except Exception:
                # Em produção você pode logar o erro
                continue

        return result

    @staticmethod
    def atualizar_dados():
        """
        Lê a carteira, busca dados na BRAPI e retorna um dicionário
        com dados de ações e FIIs separados.
        """
        carteira = AutoFetcher._get_carteira()
        if not carteira:
            return {"acoes": [], "fiis": []}

        tickers = [c[0] for c in carteira]
        brapi_data = AutoFetcher._fetch_brapi_data(tickers)

        acoes = []
        fiis = []

        for ticker, quantidade, tipo in carteira:
            dados = brapi_data.get(ticker)
            if not dados:
                continue

            preco = dados.get("regularMarketPrice")
            dy = dados.get("dividendYield")
            pvp = dados.get("priceToBook")
            lpa = dados.get("eps")
            vpa = dados.get("bookValue")
            roe = dados.get("roe")
            cagr = None  # você pode calcular depois

            item = {
                "ticker": ticker,
                "preco": preco,
                "dy": dy,
                "pvp": pvp,
                "lpa": lpa,
                "vpa": vpa,
                "roe": roe,
                "cagr": cagr,
                "valor_justo": None,
                "margem": None,
                "score": None,
            }

            if tipo == "acao":
                acoes.append(item)
            else:
                fiis.append(item)

        return {"acoes": acoes, "fiis": fiis}


if __name__ == "__main__":
    # Teste rápido
    print("Lendo carteira e consultando BRAPI...")
    dados = AutoFetcher.atualizar_dados()
    print("Ações:", len(dados["acoes"]))
    print("FIIs:", len(dados["fiis"]))
