import pandas as pd

HIST_PATH = "data/historico.csv"

class TendenciasEngine:

    @staticmethod
    def _media_movel(series, janela):
        if len(series) < janela:
            return None
        return series.tail(janela).mean()

    @staticmethod
    def _tendencia_simples(series):
        if len(series) < 3:
            return "estável"
        if series.iloc[-1] > series.iloc[-3]:
            return "alta"
        if series.iloc[-1] < series.iloc[-3]:
            return "baixa"
        return "estável"

    @staticmethod
    def gerar_tendencias():
        try:
            df = pd.read_csv(HIST_PATH, sep=";")
        except FileNotFoundError:
            return {}

        tendencias = {}

        for ticker, grupo in df.groupby("ticker"):
            grupo = grupo.sort_values("data")

            preco = grupo["price"]
            margem = grupo["margem"]
            score = grupo["score"]
            valor_justo = grupo["valor_justo"]
            dy = grupo["dy"]

            mm5 = TendenciasEngine._media_movel(preco, 5)
            mm20 = TendenciasEngine._media_movel(preco, 20)

            if mm5 and mm20:
                if mm5 > mm20:
                    sinal_preco = "tendência de alta"
                elif mm5 < mm20:
                    sinal_preco = "tendência de baixa"
                else:
                    sinal_preco = "estável"
            else:
                sinal_preco = "dados insuficientes"

            tendencias[ticker] = {
                "preco": sinal_preco,
                "margagem": TendenciasEngine._tendencia_simples(margem),
                "score": TendenciasEngine._tendencia_simples(score),
                "valor_justo": TendenciasEngine._tendencia_simples(valor_justo),
                "dy": TendenciasEngine._tendencia_simples(dy),
                "mm5": mm5,
                "mm20": mm20
            }

        return tendencias
