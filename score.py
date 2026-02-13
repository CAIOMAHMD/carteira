import math

class ScoreEngine:
    @staticmethod
    def evaluate(ativo):
        is_fii = ativo.get("is_fii", False)
        price = ativo.get("price", 0.0001)
        cagr = ativo.get("cagr", 0)
        lpa = ativo.get("lpa", 0)
        vpa = ativo.get("vpa", 0)
        dy_orig = ativo.get("dy", 0)
        payout = ativo.get("payout", 100)
        pvp = ativo.get("pvp", 0)
        roe = ativo.get("roe", 0)

        # Dados específicos de FIIs
        vacancia = ativo.get("vacancia", 0)
        tipo_fii = ativo.get("tipo_fii", "").upper()
        patrimonio_total = ativo.get("patrimonio_total", 0)
        num_cotistas = ativo.get("num_cotistas", 0)
        ultimo_rendimento = ativo.get("ultimo_rendimento", 0)
        yoc = ativo.get("yoc", 0)

        # --- 1. CONFIGURAÇÃO ANTICÍCLICA ---
        cenario = 'NEUTRO'
        
        if not is_fii:
            taxa_bazin = 0.06 if cenario == 'BULL' else (0.07 if cenario == 'BEAR' else 0.065)
            taxa_desconto_gordon = 0.12
            cap_crescimento = 0.08
        else:
            taxa_bazin = 0.08 if cenario == 'BULL' else (0.09 if cenario == 'BEAR' else 0.085)
            taxa_desconto_gordon = 0.10
            cap_crescimento = 0.015

        # --- 2. CÁLCULO DOS MODELOS ---
        dy_ajustado = dy_orig * (100 / payout) if payout > 100 else dy_orig
        div_anual = price * (dy_ajustado / 100)

        modelos_validos = {}

        # BAZIN
        if div_anual > 0:
            modelos_validos['Bazin'] = div_anual / taxa_bazin

        # GORDON
        g = min(max(0, cagr / 100), cap_crescimento)
        if div_anual > 0 and taxa_desconto_gordon > g:
            modelos_validos['Gordon'] = (div_anual * (1 + g)) / (taxa_desconto_gordon - g)

        # EXCLUSIVOS AÇÕES
        if not is_fii:
            if lpa > 0 and vpa > 0:
                modelos_validos['Graham'] = math.sqrt(22.5 * lpa * vpa)
            if cagr > 0 and lpa > 0:
                modelos_validos['Lynch'] = cagr * lpa

        # --- 3. REGRAS DE VALIDADE ---
        valor_justo = 0
        status_analise = "OK"

        if not is_fii:
            if len(modelos_validos) >= 2:
                valor_justo = sum(modelos_validos.values()) / len(modelos_validos)
            else:
                status_analise = "WATCHLIST (Modelos Insuficientes)"
        else:
            if 'Bazin' in modelos_validos and 'Gordon' in modelos_validos:
                valor_justo = (modelos_validos['Bazin'] + modelos_validos['Gordon']) / 2
            else:
                status_analise = "SEM COMPRA (Dados Incompletos)"

        # --- 4. MARGEM DE SEGURANÇA E SCORE BASE ---
        margem = ((valor_justo / price) - 1) * 100 if valor_justo > 0 else 0
        
        score = 0

        if is_fii:
            # Base: valuation
            if pvp <= 0.95: score += 4
            if dy_ajustado >= 9: score += 3
            if margem >= 17.6: score += 3

            # Vacância (só faz sentido para tijolo)
            if tipo_fii == "TIJOLO":
                if vacancia < 5: score += 2
                elif vacancia > 10: score -= 2

            # Tamanho do fundo
            if patrimonio_total >= 2_000_000_000:  # >= 2B
                score += 1

            # Número de cotistas
            if num_cotistas >= 200_000:
                score += 1

            # Último rendimento coerente com DY
            if ultimo_rendimento > 0 and price > 0:
                dy_mensal = (ultimo_rendimento / price) * 100
                if dy_mensal > 0.5:  # ~6% ao ano
                    score += 1

            # YOC alto indica bom preço de entrada
            if yoc >= 10:
                score += 1

        else:
            if pvp <= 0.90: score += 4
            if dy_ajustado >= 9: score += 4
            if roe >= 15: score += 2

        # --- 5. STATUS FINAL ---
        status = "AGUARDAR"
        if status_analise == "OK" and valor_justo > 0:
            if is_fii:
                if score >= 8 and pvp <= 0.95 and margem >= 17.6:
                    status = "FORTE COMPRA"
                elif pvp <= 0.98 and dy_ajustado >= 8.5:
                    status = "COMPRA"
            else:
                if pvp <= 0.90 and dy_ajustado >= 9 and margem >= 15:
                    status = "FORTE COMPRA"
                elif pvp <= 0.95 and dy_ajustado >= 8:
                    status = "COMPRA"
        
        if status == "AGUARDAR" and score >= 5:
            status = "NEUTRO"
        if "WATCHLIST" in status_analise:
            status = "WATCHLIST"

        return {
            **ativo,
            "graham": modelos_validos.get('Graham', 0),
            "bazin": modelos_validos.get('Bazin', 0),
            "lynch": modelos_validos.get('Lynch', 0),
            "valor_justo": valor_justo,
            "margem": margem,
            "score": score,
            "status": status,
            "crescimento_status": "🟢 CONSISTENTE" if cagr > 7 else ("🔴 NEGATIVO" if cagr < 0 else "🟡 INSTÁVEL")
        }
