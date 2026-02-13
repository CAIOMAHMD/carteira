import math

MODOS_RISCO = {
    "conservador": {
        "peso_score": 0.8,
        "peso_pvp": 0.6,
        "peso_dy": 0.7,
        "peso_status": 1.0,
        "peso_tijolo": 1.2,
        "peso_papel": 0.7,
        "peso_acoes": 1.6,
        "limite_concentracao": 0.25,
        "limite_fiis_max": 0.60,
        "limite_acoes_min": 0.25
    },
    "moderado": {
        "peso_score": 1.0,
        "peso_pvp": 0.6,
        "peso_dy": 0.8,
        "peso_status": 1.0,
        "peso_tijolo": 1.0,
        "peso_papel": 1.0,
        "peso_acoes": 1.8,
        "limite_concentracao": 0.35,
        "limite_fiis_max": 0.70,
        "limite_acoes_min": 0.20
    },
    "agressivo": {
        "peso_score": 1.3,
        "peso_pvp": 0.8,
        "peso_dy": 1.0,
        "peso_status": 1.2,
        "peso_tijolo": 1.0,
        "peso_papel": 1.3,
        "peso_acoes": 1.4,
        "limite_concentracao": 0.45,
        "limite_fiis_max": 0.80,
        "limite_acoes_min": 0.10
    }
}


class InvestmentEngine:

    def __init__(self, modo="moderado"):
        if modo not in MODOS_RISCO:
            raise ValueError(f"Modo de risco inválido: {modo}")
        self.modo = modo
        self.m = MODOS_RISCO[modo]

    # -----------------------------
    # CÁLCULO DE PESOS
    # -----------------------------
    def _peso_base(self, d):
        score = max(0, d.get("score", 0))
        return (score ** 2) * self.m["peso_score"]

    def _peso_fii(self, d):
        m = self.m
        fator = 1.0

        pvp = d.get('pvp', 1) or 1
        dy = d.get('dy', 0) or 0
        tipo = d.get('tipo_fii', "TIJOLO")
        status = d.get("status", "")

        # P/VP – curva mais suave e menos dominante
        try:
            impacto_pvp = max(0, math.log(1 / pvp)) * m["peso_pvp"]
        except ValueError:
            impacto_pvp = 0
        fator += impacto_pvp

        # DY – suavizado (raiz) para não explodir
        if dy > 0:
            impacto_dy = (dy / 12) ** 0.5 * m["peso_dy"]
            fator += impacto_dy

        # Tipo do FII
        if tipo.upper() == "TIJOLO":
            fator *= m["peso_tijolo"]
        else:
            fator *= m["peso_papel"]

        # Status
        if status == "FORTE COMPRA":
            fator *= 1.2 * m["peso_status"]
        elif status == "COMPRA":
            fator *= 1.0 * m["peso_status"]

        return max(fator, 0.1)

    def _peso_acao(self, d):
        m = self.m
        margem = d.get('margem', 0) or 0
        fator = 1.0 + max(0, margem / 100)
        fator *= m["peso_acoes"]
        return max(fator, 0.1)

    # -----------------------------
    # BALANCEAMENTO FIIs x AÇÕES
    # -----------------------------
    def _balancear_classes(self, pesos):
        m = self.m
        limite_fiis_max = m["limite_fiis_max"]
        limite_acoes_min = m["limite_acoes_min"]

        total = sum(p for _, p in pesos)
        if total <= 0:
            return pesos

        total_fiis = sum(p for d, p in pesos if d.get("is_fii"))
        total_acoes = total - total_fiis

        if total_acoes <= 0:
            # Não há ações elegíveis → não força nada
            return pesos

        frac_fiis = total_fiis / total
        frac_acoes = total_acoes / total

        fator_fiis = fator_acoes = 1.0

        # Se FIIs passaram do máximo, reduz
        if frac_fiis > limite_fiis_max and total_fiis > 0:
            alvo_fiis = limite_fiis_max * total
            fator_fiis = alvo_fiis / total_fiis

        # Se ações estão abaixo do mínimo, aumenta
        if frac_acoes < limite_acoes_min and total_acoes > 0:
            alvo_acoes = limite_acoes_min * total
            fator_acoes = alvo_acoes / total_acoes

        novos_pesos = []
        for d, p in pesos:
            if d.get("is_fii"):
                novos_pesos.append((d, p * fator_fiis))
            else:
                novos_pesos.append((d, p * fator_acoes))

        return novos_pesos

    # -----------------------------
    # LIMITE DE CONCENTRAÇÃO
    # -----------------------------
    def _aplicar_limite_concentracao(self, pesos):
        m = self.m
        total = sum(p for _, p in pesos)
        if total <= 0:
            return pesos

        limite = m["limite_concentracao"] * total
        novos = []
        for d, p in pesos:
            if p > limite:
                p = limite
            novos.append((d, p))
        return novos

    # -----------------------------
    # DISTRIBUIÇÃO DO APORTE
    # -----------------------------
    def _distribuir_aporte(self, pesos, aporte_total):
        if aporte_total <= 0 or not pesos:
            return {"sugestoes": [], "caixa_residual": aporte_total}

        total_pesos = sum(p for _, p in pesos)
        if total_pesos <= 0:
            return {"sugestoes": [], "caixa_residual": aporte_total}

        sugestoes = {}
        caixa_alocado = 0

        # 1ª passada – alocação proporcional
        for d, peso in pesos:
            ticker = d["ticker"]
            price = d["price"]
            if price <= 0:
                continue

            verba = aporte_total * (peso / total_pesos)
            cotas = int(verba // price)

            if cotas > 0:
                valor = cotas * price
                caixa_alocado += valor
                sugestoes[ticker] = {
                    "ticker": ticker,
                    "cotas": cotas,
                    "valor": valor,
                    "price": price
                }

        caixa_restante = aporte_total - caixa_alocado

        # 2ª passada – arremate por menor preço
        ativos_arremate = sorted(
            sugestoes.values(),
            key=lambda x: x['price']
        )

        for s in ativos_arremate:
            while caixa_restante >= s['price']:
                s['cotas'] += 1
                s['valor'] += s['price']
                caixa_restante -= s['price']

        return {
            "sugestoes": list(sugestoes.values()),
            "caixa_residual": round(caixa_restante, 2)
        }

    # -----------------------------
    # MÉTODO PRINCIPAL
    # -----------------------------
    def calculate_allocation(self, data, aporte_total):
        # Filtrar ativos elegíveis
        oportunidades = [
            d for d in data
            if d.get("status") in ["COMPRA", "FORTE COMPRA"]
        ]

        if not oportunidades or aporte_total <= 0:
            return {"sugestoes": [], "caixa_residual": aporte_total}

        pesos = []
        for d in oportunidades:
            base = self._peso_base(d)
            if d.get("is_fii"):
                fator = self._peso_fii(d)
            else:
                fator = self._peso_acao(d)
            pesos.append((d, base * fator))

        # Balancear FIIs x Ações (máx FIIs, mín ações)
        pesos = self._balancear_classes(pesos)

        # Limitar concentração por ativo
        pesos = self._aplicar_limite_concentracao(pesos)

        # Distribuir aporte
        return self._distribuir_aporte(pesos, aporte_total)
