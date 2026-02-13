from engine.analyzer import PortfolioAnalyzer

class Exporter:
    @staticmethod
    def export_html(
        acoes,
        fiis,
        path,
        sugestao_aporte,
        tendencias_ativos=None,
        alertas=None,
        riscos=None
    ):
        todos = acoes + fiis
        media_s = sum(x['score'] for x in todos) / len(todos) if todos else 0
        termometro = "⚖️ NEUTRO" if 4 <= media_s <= 7 else ("🔥 CARO" if media_s < 4 else "❄️ OPORTUNO")

        tendencia = PortfolioAnalyzer.get_trend_data()

        def fmt_delta(val):
            if val == 0:
                return '<span style="color: #718096; font-size: 11px;">(0.0%)</span>'
            cor = "#2f855a" if val > 0 else "#c53030"
            seta = "▲" if val > 0 else "▼"
            return f'<span style="color: {cor}; font-size: 11px; font-weight: bold;">{seta} {abs(val):.1f}%</span>'

        html_cards_evolucao = ""
        if tendencia:
            html_cards_evolucao = f"""
                <div class="card">Evolução Score<br>
                    <b style="font-size: 18px;">{tendencia['score_atual']:.1f}</b><br>{fmt_delta(tendencia['score_delta'])}
                </div>
                <div class="card">Evolução DY Médio<br>
                    <b style="font-size: 18px;">{tendencia['dy_atual']:.2f}%</b><br>{fmt_delta(tendencia['dy_delta'])}
                </div>
            """

        # ------------------------------------------------------------
        # HTML PRINCIPAL
        # ------------------------------------------------------------
        html = f"""
        <html><head><meta charset="UTF-8"><style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 25px; font-size: 12px; color: #333; }}
            h1, h2 {{ color: #2c3e50; border-bottom: 2px solid #3182ce; padding-bottom: 5px; margin-top: 25px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; margin-bottom: 20px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            th, td {{ padding: 12px; border: 1px solid #e2e8f0; text-align: center; font-size: 12px; }}
            th {{ background: #2d3748; color: white; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }}
            
            .ticker {{ font-weight: bold; color: #3182ce; }}
            .col-valuation {{ background-color: #fffaf0 !important; color: #744210 !important; }}
            .v-justo-celula {{ background-color: #ebf8ff !important; color: #2c5282 !important; font-weight: bold !important; border-left: 2px solid #3182ce !important; }}
            
            .status-forte-compra {{ background: #276749 !important; color: white; font-weight: bold; }}
            .status-compra {{ background: #48bb78 !important; color: white; }}
            .status-neutro {{ background: #edf2f7 !important; }}
            .status-aguardar {{ background: #fff5f5 !important; color: #c53030; }}
            
            .card {{ background: white; padding: 15px; border-radius: 10px; display: inline-block; margin-right: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; min-width: 120px; vertical-align: top; }}
            .positivo {{ color: #2f855a; font-weight: bold; }}
            .negativo {{ color: #c53030; font-weight: bold; }}
        </style></head><body>
            <h1>📈 Matrix Invest Analyzer PRO (v.2026)</h1>
            
            <div style="margin-bottom: 20px;">
                <div class="card">Termômetro<br><b style="font-size: 18px;">{termometro}</b></div>
                <div class="card">Score Médio<br><b style="font-size: 18px;">{media_s:.1f}</b></div>
                {html_cards_evolucao}
            </div>
        """

        # ------------------------------------------------------------
        # ALERTAS
        # ------------------------------------------------------------
        if alertas:
            html += """
            <h2>🔔 Alertas Inteligentes</h2>
            <ul style='background: #fff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
            """
            for a in alertas:
                html += f"<li style='margin-bottom: 6px;'>{a}</li>"
            html += "</ul>"

        # ------------------------------------------------------------
        # AÇÕES
        # ------------------------------------------------------------
        html += """
            <h2>💼 Ações - Detalhes de Valuation</h2>
            <table>
                <tr>
                    <th>Ticker</th><th>Crescimento</th><th>Preço</th>
                    <th class="col-valuation">Graham</th><th class="col-valuation">Bazin</th><th class="col-valuation">Lynch</th>
                    <th class="v-justo-celula">V. Justo</th><th>Margem</th><th>Score</th><th>Status</th>
                </tr>
        """

        for a in acoes:
            st_css = "status-" + a['status'].lower().replace(" ", "-")
            m_cor = "positivo" if a['margem'] > 0 else "negativo"
            html += f"""
                <tr>
                    <td class="ticker">{a['ticker']}</td>
                    <td>{a['crescimento_status']}</td>
                    <td>R$ {a['price']:.2f}</td>
                    <td class="col-valuation">R$ {a.get('graham', 0):.2f}</td>
                    <td class="col-valuation">R$ {a.get('bazin', 0):.2f}</td>
                    <td class="col-valuation">R$ {a.get('lynch', 0):.2f}</td>
                    <td class="v-justo-celula">R$ {a['valor_justo']:.2f}</td>
                    <td class="{m_cor}">{a['margem']:.1f}%</td>
                    <td>{a['score']}</td>
                    <td class="{st_css}">{a['status']}</td>
                </tr>"""

        html += """
            </table>
        """

        # ------------------------------------------------------------
        # FIIs
        # ------------------------------------------------------------
        html += """
            <h2>🏢 Fundos Imobiliários</h2>
            <table>
                <tr><th>Ticker</th><th>Preço</th><th>P/VP</th><th>DY</th><th class="v-justo-celula">V. Justo</th><th>Score</th><th>Status</th></tr>
        """

        for f in fiis:
            st_css = "status-" + f['status'].lower().replace(" ", "-")
            html += f"""
                <tr>
                    <td class="ticker">{f['ticker']}</td>
                    <td>R$ {f['price']:.2f}</td>
                    <td>{f['pvp']:.2f}</td>
                    <td>{f['dy']:.2f}%</td>
                    <td class="v-justo-celula">R$ {f['valor_justo']:.2f}</td>
                    <td>{f['score']}</td>
                    <td class="{st_css}">{f['status']}</td>
                </tr>"""

        html += "</table>"

        # ------------------------------------------------------------
        # SUGESTÃO DE APORTE
        # ------------------------------------------------------------
        html += """
            <h2 style='color: #2b6cb0;'>💰 Plano de Aporte Oportunista</h2>
            <table>
                <tr><th>Ativo</th><th>Cotas a Comprar</th><th>Investimento Estimado</th></tr>
        """

        for s in sugestao_aporte.get('sugestoes', []):
            html += f"""
                <tr>
                    <td class="ticker">{s['ticker']}</td>
                    <td style='font-size: 16px; font-weight: bold;'>{s['cotas']}</td>
                    <td>R$ {s['valor']:.2f}</td>
                </tr>"""

        html += f"""
            </table>
            <div class="card" style="background: #ebf8ff; border: 1px solid #3182ce; min-width: 300px;">
                <span style="color: #2c5282;">Caixa Residual Próximo Aporte:</span><br>
                <b style="font-size: 22px; color: #2b6cb0;">R$ {sugestao_aporte.get('caixa_residual', 0):.2f}</b>
            </div>
        """

        # ------------------------------------------------------------
        # TENDÊNCIAS POR ATIVO
        # ------------------------------------------------------------
        if tendencias_ativos:
            html += """
                <h2>📉 Tendências por Ativo</h2>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Preço</th>
                        <th>Margem</th>
                        <th>Score</th>
                        <th>DY</th>
                    </tr>
            """
            for t, tend in tendencias_ativos.items():
                html += f"""
                    <tr>
                        <td class="ticker">{t}</td>
                        <td>{tend.get('preco')}</td>
                        <td>{tend.get('margem')}</td>
                        <td>{tend.get('score')}</td>
                        <td>{tend.get('dy')}</td>
                    </tr>
                """
            html += "</table>"

        # ------------------------------------------------------------
        # RISCO POR ATIVO
        # ------------------------------------------------------------
        if riscos:
            html += """
                <h2>⚠️ Risco por Ativo</h2>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Volatilidade</th>
                        <th>Drawdown</th>
                        <th>Tendência</th>
                        <th>Fundamentos</th>
                        <th>Classe</th>
                        <th>Concentração</th>
                        <th>Risco Total</th>
                    </tr>
            """
            for t, r in riscos.items():
                html += f"""
                    <tr>
                        <td class="ticker">{t}</td>
                        <td>{r['volatilidade']:.2f}%</td>
                        <td>{r['drawdown']:.2f}%</td>
                        <td>{r['risco_tendencia']}</td>
                        <td>{r['risco_fundamentos']}</td>
                        <td>{r['risco_classe']}</td>
                        <td>{r['risco_concentracao']}</td>
                        <td><b>{r['risco_total']:.2f}</b></td>
                    </tr>
                """
            html += "</table>"

        html += """
            <style>
                .btn-voltar {
                    display: inline-block;
                    padding: 12px 22px;
                    background: linear-gradient(135deg, #3182ce, #2b6cb0);
                    color: white;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 14px;
                    box-shadow: 0 4px 10px rgba(49,130,206,0.3);
                    transition: all 0.25s ease-in-out;
                }

                .btn-voltar:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 8px 18px rgba(49,130,206,0.45);
                    background: linear-gradient(135deg, #2b6cb0, #2c5282);
                }

                .btn-voltar:active {
                    transform: translateY(0px);
                    box-shadow: 0 4px 10px rgba(49,130,206,0.3);
                }
            </style>

            <div style="text-align:center; margin-top: 40px;">
                <a href="/" class="btn-voltar">
                    ⬅ Voltar para a Carteira
                </a>
            </div>

            <p style="color: #718096; font-size: 11px; margin-top: 30px; text-align: center;">
                Meta: Aposentadoria aos 50 anos | Caio Portfolio Management
            </p>
        </body></html>
        """


        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
