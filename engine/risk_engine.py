import pandas as pd

HIST_PATH = "data/historico.csv"

class RiskEngine:

    @staticmethod
    def _volatilidade(series):
        if len(series) < 5:
            return 0
        retornos = series.pct_change().dropna()
        return float(retornos.std() * 100)

    @staticmethod
    def _drawdown(series):
        if len(series) < 5:
            return 0
        max_acum = series.cummax()
        dd = (series - max_acum) / max_acum
        return float(dd.min() * 100)

    @staticmethod
    def _risco_tendencia(tend):
        if tend == "tendência de baixa":
            return 30
        if tend == "baixa":
            return 20
        if tend == "estável":
            return 10
        if tend in ["alta", "tendência de alta"]:
            return 5
        return 10

    @staticmethod
    def _risco_fundamentos(ativo):
        risco = 0

        if ativo.get("score", 0) < 4:
            risco += 25
        elif ativo.get("score", 0) < 6:
            risco += 10

        if ativo.get("margem", 0) < 0:
            risco += 20

        if ativo.get("valor_justo", 0) < ativo.get("price", 0):
            risco += 10

        return risco

    @staticmethod
    def _risco_classe(ativo):
        return 10 if ativo.get("is_fii") else 20

    @staticmethod
    def _risco_concentracao(peso, total_pesos):
        frac = peso / total_pesos if total_pesos > 0 else 0
        if frac > 0.25:
            return 25
        if frac > 0.15:
            return 10
        return 5

    @staticmethod
    def calcular_risco(avaliados, tendencias_ativos):
        try:
            df = pd.read_csv(HIST_PATH, sep=";")
        except:
            return {}

        riscos = {}
        total_pesos = sum(a.get("score", 1) for a in avaliados)

        for ativo in avaliados:
            ticker = ativo["ticker"]
            grupo = df[df["ticker"] == ticker].sort_values("data")

            preco = grupo["price"] if "price" in grupo else pd.Series()

            volatilidade = RiskEngine._volatilidade(preco)
            drawdown = RiskEngine._drawdown(preco)

            tend = tendencias_ativos.get(ticker, {})
            risco_tend = RiskEngine._risco_tendencia(tend.get("preco", "estável"))

            risco_fund = RiskEngine._risco_fundamentos(ativo)
            risco_classe = RiskEngine._risco_classe(ativo)
            risco_conc = RiskEngine._risco_concentracao(
                ativo.get("score", 1),
                total_pesos
            )

            risco_total = (
                volatilidade * 0.4 +
                abs(drawdown) * 0.3 +
                risco_tend * 0.2 +
                risco_fund * 0.3 +
                risco_classe * 0.1 +
                risco_conc * 0.2
            )

            riscos[ticker] = {
                "volatilidade": round(volatilidade, 2),
                "drawdown": round(drawdown, 2),
                "risco_tendencia": risco_tend,
                "risco_fundamentos": risco_fund,
                "risco_classe": risco_classe,
                "risco_concentracao": risco_conc,
                "risco_total": round(risco_total, 2)
            }

        return riscos
