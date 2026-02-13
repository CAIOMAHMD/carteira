import csv
import os

class DataFetcher:
    @staticmethod
    def _clean_val(val):
        if not val or val == '-': return 0.0
        try:
            # Remove %, R$ e troca vírgula por ponto
            clean = str(val).replace('%', '').replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(clean)
        except:
            return 0.0

    @staticmethod
    def get_local_data():
        results = []
        
        # --- PROCESSANDO AÇÕES ---
        path_acoes = 'data/acoes.csv'
        if os.path.exists(path_acoes):
            with open(path_acoes, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    # O pulo do gato: mapear o que é o que baseado no seu CSV real
                    results.append({
                        "ticker": row.get("Ticker", "???").upper(),
                        "price": DataFetcher._clean_val(row.get("Preço Atual", 0)),
                        "dy": DataFetcher._clean_val(row.get("DY 12 Meses", 0)),
                        "payout": DataFetcher._clean_val(row.get("Payout", 0)),
                        "pvp": DataFetcher._clean_val(row.get("PVP", 0)),
                        "roe": DataFetcher._clean_val(row.get("ROE", 0)),
                        # Baseado no seu CSV, LPA e VPA parecem estar deslocados ou precisam ser calculados
                        # Se o seu CSV não tem coluna 'LPA', vamos usar o PL para deduzir: LPA = Preço / PL
                        "lpa": DataFetcher._clean_val(row.get("Preço Atual", 0)) / DataFetcher._clean_val(row.get("PL", 1)) if DataFetcher._clean_val(row.get("PL", 0)) != 0 else 0,
                        "vpa": DataFetcher._clean_val(row.get("Preço Atual", 0)) / DataFetcher._clean_val(row.get("PVP", 1)) if DataFetcher._clean_val(row.get("PVP", 0)) != 0 else 0,
                        "cagr": DataFetcher._clean_val(row.get("CAGR Lucro", 0)),
                        "is_fii": False
                    })

        # --- PROCESSANDO FIIS ---
        path_fiis = 'data/fiis.csv'
        if os.path.exists(path_fiis):
            with open(path_fiis, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    results.append({
                        "ticker": row.get("Ticker", "???").upper(),
                        "price": DataFetcher._clean_val(row.get("Preço Atual", 0)),
                        "pvp": DataFetcher._clean_val(row.get("P/VP", 0)),
                        "dy": DataFetcher._clean_val(row.get("DY 12 Meses", 0)),
                        "yoc": DataFetcher._clean_val(row.get("Yield On Cost", 0)),
                        "is_fii": True
                    })
        
        return results