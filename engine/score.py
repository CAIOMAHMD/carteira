import math

class ScoreEngine:

    @staticmethod
    def evaluate(ativo):

        # ============================================================
        # 1. NORMALIZAÇÃO DOS DADOS
        # ============================================================

        is_fii = ativo.get("is_fii", False)

        price = float(ativo.get("price", 0))
        dy = float(ativo.get("dy", 0))
        pvp = float(ativo.get("pvp", 0))
        payout = float(ativo.get("payout", 0))
        cagr = float(ativo.get("cagr", 0))
        lpa = float(ativo.get("lpa", 0))
        vpa = float(ativo.get("vpa", 0))
        roe = float(ativo.get("roe", 0))

        # FIIs
        vacancia = float(ativo.get("vacancia", 0))
        tipo_fii = ativo.get("tipo_fii", "").upper()
        patrimonio_total = float(ativo.get("patrimonio_total", 0))
        num_cotistas = float(ativo.get("num_cotistas", 0))
        ultimo_rendimento = float(ativo.get("ultimo_rendimento", 0))

        # ============================================================
        # 2. AJUSTES DE ESCALA
        # ============================================================

        if payout < 1:
            payout *= 100

        dy_ajustado = dy * (100 / payout) if payout > 0 else dy

        # DY limitado para evitar distorções
        dy_limite = min(dy_ajustado, 15)

        div_anual = price * (dy_limite / 100)

        # ============================================================
        # 3. MODELOS DE VALUATION
        # ============================================================

        modelos = {}

        # Taxas
        taxa_bazin = 0.065 if not is_fii else 0.085
        taxa_desconto = 0.12 if not is_fii else 0.10
        cap_crescimento = 0.08 if not is_fii else 0.015

        # Bazin
        if div_anual > 0:
            modelos["Bazin"] = div_anual / taxa_bazin

        # Gordon
        g = min(max(0, cagr / 100), cap_crescimento)
        if div_anual > 0 and taxa_desconto > g:
            modelos["Gordon"] = (div_anual * (1 + g)) / (taxa_desconto - g)

        # Graham (ações)
        if not is_fii and lpa > 0 and vpa > 0:
            modelos["Graham"] = math.sqrt(22.5 * lpa * vpa)

        # Lynch (ações)
        if not is_fii and cagr > 0 and lpa > 0:
            modelos["Lynch"] = lpa * (cagr / 100)

        # ============================================================
        # 4. VALOR JUSTO (MÉDIA PONDERADA)
        # ============================================================

        pesos = {
            "Bazin": 0.35,
            "Gordon": 0.25,
            "Graham": 0.25,
            "Lynch": 0.15
        }

        valor_justo = 0
        peso_total = 0

        for nome, val in modelos.items():
            valor_justo += val * pesos.get(nome, 0)
            peso_total += pesos.get(nome, 0)

        valor_justo = valor_justo / peso_total if peso_total > 0 else 0

        margem = ((valor_justo / price) - 1) * 100 if valor_justo > 0 else 0

        # ============================================================
        # 5. SCORE INTELIGENTE
        # ============================================================

        score = 0

        # -------------------------
        # AÇÕES
        # -------------------------
        if not is_fii:

            # Valuation
            if margem >= 20: score += 3
            elif margem >= 10: score += 2
            elif margem >= 0: score += 1

            # Qualidade
            if roe >= 12: score += 2
            if pvp <= 1.2: score += 1

            # Crescimento
            if cagr >= 8: score += 2
            elif cagr >= 3: score += 1

            # Dividendos
            if dy >= 6: score += 2
            elif dy >= 3: score += 1

        # -------------------------
        # FIIs
        # -------------------------
        else:

            # Valuation
            if pvp <= 0.90: score += 3
            elif pvp <= 0.95: score += 2

            if margem >= 15: score += 2

            # Vacância
            if tipo_fii == "TIJOLO":
                if vacancia < 5: score += 2
                elif vacancia > 10: score -= 2

            # Tamanho
            if patrimonio_total >= 1_000_000_000:
                score += 1

            # Cotistas
            if num_cotistas >= 50_000:
                score += 1

            # Rendimento mensal
            if ultimo_rendimento > 0:
                dy_mensal = (ultimo_rendimento / price) * 100
                if dy_mensal >= 0.5:
                    score += 1

        # ============================================================
        # 6. STATUS FINAL
        # ============================================================

        status = "AGUARDAR"

        if score >= 9 and margem >= 20:
            status = "FORTE COMPRA"
        elif score >= 6:
            status = "COMPRA"
        elif score >= 4:
            status = "NEUTRO"

        return {
            **ativo,
            "graham": modelos.get("Graham", 0),
            "bazin": modelos.get("Bazin", 0),
            "lynch": modelos.get("Lynch", 0),
            "valor_justo": valor_justo,
            "margem": margem,
            "score": score,
            "status": status,
            "crescimento_status": (
                "🟢 CONSISTENTE" if cagr > 7 else
                "🔴 NEGATIVO" if cagr < 0 else
                "🟡 INSTÁVEL"
            )
        }
