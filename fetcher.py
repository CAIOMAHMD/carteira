import csv
import os

class DataFetcher:
    @staticmethod
    def _clean_val(val):
        if not val or val == '-':
            return 0.0

        clean = str(val).replace('%', '').replace('R$', '').strip()

        # Converte bilhões e milhões (ex: 9.7B, 3.2B, 250M)
        if clean.endswith('B'):
            num = clean[:-1].replace('.', '').replace(',', '.')
            try:
                return float(num) * 1_000_000_000
            except:
                return 0.0

        if clean.endswith('M'):
            num = clean[:-1].replace('.', '').replace(',', '.')
            try:
                return float(num) * 1_000_000
            except:
                return 0.0

        # Remove separador de milhar e troca vírgula por ponto
        clean = clean.replace('.', '').replace(',', '.')

        try:
            return float(clean)
        except:
            return 0.0

    @staticmethod
    def get_local_data():
        results = []
        
        # --- PROCESSANDO AÇÕES (NÃO ALTERAR) ---
        path_acoes = 'data/acoes.csv'
        if os.path.exists(path_acoes):
            with open(path_acoes, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    results.append({
                        "ticker": row.get("Ticker", "???").upper(),
                        "price": DataFetcher._clean_val(row.get("Preço Atual", 0)),
                        "dy": DataFetcher._clean_val(row.get("DY 12 Meses", 0)),
                        "payout": DataFetcher._clean_val(row.get("Payout", 0)),
                        "pvp": DataFetcher._clean_val(row.get("PVP", 0)),
                        "roe": DataFetcher._clean_val(row.get("ROE", 0)),
                        "lpa": DataFetcher._clean_val(row.get("Preço Atual", 0)) / DataFetcher._clean_val(row.get("PL", 1)) if DataFetcher._clean_val(row.get("PL", 0)) != 0 else 0,
                        "vpa": DataFetcher._clean_val(row.get("Preço Atual", 0)) / DataFetcher._clean_val(row.get("PVP", 1)) if DataFetcher._clean_val(row.get("PVP", 0)) != 0 else 0,
                        "cagr": DataFetcher._clean_val(row.get("CAGR Lucro", 0)),
                        "is_fii": False
                    })

        # --- PROCESSANDO FIIS (ATUALIZADO) ---
        path_fiis = 'data/fiis.csv'
        if os.path.exists(path_fiis):
            with open(path_fiis, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    tipo = (row.get("TIPO", "") or "").strip().lower()

                    results.append({
                        "ticker": row.get("Ticker", "???").upper(),
                        "price": DataFetcher._clean_val(row.get("PreçoAtual", 0)),
                        "pvp": DataFetcher._clean_val(row.get("PVP", 0)),
                        "dy": DataFetcher._clean_val(row.get("DY12Meses", 0)),
                        "yoc": DataFetcher._clean_val(row.get("YieldOnCost", 0)),
                        "vacancia": DataFetcher._clean_val(row.get("Vacancia", 0)),
                        "vp_cota": DataFetcher._clean_val(row.get("ValorPatrimonialCota", 0)),
                        "ultimo_rendimento": DataFetcher._clean_val(row.get("UltimoRendimento", 0)),
                        "patrimonio_total": DataFetcher._clean_val(row.get("PatrimonioTotal", 0)),
                        "num_cotistas": DataFetcher._clean_val(row.get("NumeroCotistas", 0)),
                        "cotas_emitidas": DataFetcher._clean_val(row.get("CotasEmitidas", 0)),
                        "rentabilidade": DataFetcher._clean_val(row.get("Rentabilidade", 0)),
                        "variacao": DataFetcher._clean_val(row.get("Variacao", 0)),
                        "tipo_fii": "PAPEL" if "papel" in tipo else "TIJOLO",
                        "is_fii": True,

                        # Mantém compatibilidade com ScoreEngine
                        "cagr": 0.0,
                        "lpa": 0.0,
                        "vpa": DataFetcher._clean_val(row.get("ValorPatrimonialCota", 0)),
                        "payout": 100.0,
                        "roe": 0.0
                    })
        
        return results
