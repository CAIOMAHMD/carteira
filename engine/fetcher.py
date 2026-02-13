import pandas as pd

class DataFetcher:

    @staticmethod
    def get_local_data():

        try:
            acoes = pd.read_csv("data/acoes-processado.csv", sep=";")
        except:
            acoes = pd.DataFrame()

        try:
            fiis = pd.read_csv("data/fiis-processado.csv", sep=";")
        except:
            fiis = pd.DataFrame()

        dados = []

        # ============================
        # AÇÕES
        # ============================
        for _, row in acoes.iterrows():
            dados.append({
                "ticker": row.get("ticker", "???"),
                "price": row.get("price", 0),
                "dy": row.get("dy", 0),
                "payout": row.get("payout", 0),
                "pvp": row.get("pvp", 0),
                "roe": row.get("roe", 0),
                "lpa": row.get("lpa", 0),
                "vpa": row.get("vpa", 0),
                "cagr": row.get("cagr", 0),
                "is_fii": False
            })

        # ============================
        # FIIs
        # ============================
        for _, row in fiis.iterrows():
            dados.append({
                "ticker": row.get("ticker", "???"),
                "price": row.get("price", 0),
                "dy": row.get("dy", 0),
                "pvp": row.get("pvp", 0),
                "vacancia": row.get("vacancia", 0),
                "vpa": row.get("vpa", 0),
                "ultimo_rendimento": row.get("ultimo_rendimento", 0),
                "patrimonio_total": row.get("patrimonio_total", 0),
                "num_cotistas": row.get("num_cotistas", 0),
                "cotas_emitidas": row.get("cotas_emitidas", 0),
                "tipo_fii": row.get("tipo_fii", "TIJOLO"),
                "is_fii": True
            })

        return dados
