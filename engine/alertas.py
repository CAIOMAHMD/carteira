class AlertasEngine:

    @staticmethod
    def gerar_alertas(avaliados, tendencias_ativos, tendencia_carteira):
        alertas = []

        # ALERTAS POR ATIVO
        for ativo in avaliados:
            ticker = ativo["ticker"]
            t = tendencias_ativos.get(ticker, {})

            if t.get("score") == "baixa":
                alertas.append(f"⚠️ {ticker}: Score em queda.")

            if t.get("margem") == "alta":
                alertas.append(f"🟢 {ticker}: Margem aumentando — ativo ficando mais barato.")

            if t.get("preco") == "tendência de baixa":
                alertas.append(f"📉 {ticker}: Preço em tendência de baixa.")

            if t.get("preco") == "tendência de alta":
                alertas.append(f"📈 {ticker}: Preço em tendência de alta.")

            if t.get("valor_justo") == "baixa":
                alertas.append(f"⚠️ {ticker}: Valor justo caindo.")

            if t.get("dy") == "alta":
                alertas.append(f"💰 {ticker}: DY em alta.")

        # ALERTAS DA CARTEIRA
        if tendencia_carteira:
            score_delta = tendencia_carteira.get("score_delta", 0)
            dy_delta = tendencia_carteira.get("dy_delta", 0)

            if score_delta < -2:
                alertas.append("⚠️ Score médio da carteira caiu.")

            if score_delta > 2:
                alertas.append("🟢 Score médio da carteira subiu.")

            if dy_delta > 2:
                alertas.append("💰 DY médio da carteira subiu.")

            if dy_delta < -2:
                alertas.append("📉 DY médio da carteira caiu.")

        return alertas
