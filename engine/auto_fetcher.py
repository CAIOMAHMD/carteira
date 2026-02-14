import requests
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "/app/web/carteira.db"



# ============================================================
# CONFIGURAÇÃO DA BRAPI
# ============================================================
BRAPI_TOKEN = "COLOQUE_SUA_API_KEY_AQUI"   # <<< IMPORTANTE
BRAPI_URL = "https://brapi.dev/api/quote/{}?token={}&range=1d&interval=1d&fundamental=true"


class AutoFetcher:

    # ============================================================
    # LER CARTEIRA DO BANCO
    # ============================================================
    @staticmethod
    def _get_carteira():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT ticker, quantidade, tipo FROM carteira")
        dados = c.fetchall()
        conn.close()
        return dados

    # ============================================================
    # NORMALIZADORES
    # ============================================================
    @staticmethod
    def _normalizar_preco(v):
        try:
            return round(float(v), 2)
        except:
            return 0.0

    @staticmethod
    def _normalizar_percentual(v):
        try:
            return round(float(v) * 100, 2)
        except:
            return 0.0

    # ============================================================
    # BUSCAR DADOS NA BRAPI
    # ============================================================
    @staticmethod
    def _buscar_brapi(ticker):
        try:
            url = BRAPI_URL.format(ticker, BRAPI_TOKEN)
            r = requests.get(url, timeout=10)
            data = r.json()

            if "results" not in data or len(data["results"]) == 0:
                print(f"⚠️ BRAPI não retornou dados para {ticker}")
                return None

            return data["results"][0]

        except Exception as e:
            print(f"❌ Erro BRAPI {ticker}: {e}")
            return None

    # ============================================================
    # ATUALIZAR DADOS (BRAPI APENAS)
    # ============================================================
    @staticmethod
    def atualizar_dados():
        print("Atualizando dados de mercado...")

        carteira = AutoFetcher._get_carteira()
        resultados = {}

        for ticker, quant, tipo in carteira:
            print(f"🔎 Buscando dados de {ticker}...")

            api = AutoFetcher._buscar_brapi(ticker)

            if not api:
                print(f"⚠️ Sem dados para {ticker}, ignorando.")
                continue

            preco = AutoFetcher._normalizar_preco(api.get("regularMarketPrice", 0))
            dy = AutoFetcher._normalizar_percentual(api.get("dividendYield", 0))
            pvp = api.get("priceToBook", 0)
            lpa = api.get("earningsPerShare", 0)
            vpa = api.get("bookValuePerShare", 0)
            roe = AutoFetcher._normalizar_percentual(api.get("returnOnEquity", 0))
            cagr = AutoFetcher._normalizar_percentual(api.get("revenueGrowth", 0))

            resultados[ticker] = {
                "ticker": ticker,
                "quant": quant,
                "tipo": tipo,
                "preco": preco,
                "dy": dy,
                "pvp": pvp,
                "lpa": lpa,
                "vpa": vpa,
                "roe": roe,
                "cagr": cagr,
            }

        return resultados
