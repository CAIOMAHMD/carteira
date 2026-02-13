import csv
import os
from datetime import datetime

class HistoryManager:
    @staticmethod
    def save_snapshot(avaliados):
        path = "data/historico.csv"
        file_exists = os.path.isfile(path)
        data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(path, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            
            # Cabeçalho padronizado (sem acentos e incluindo o DY para o Analyzer)
            if not file_exists:
                writer.writerow(["data", "ticker", "score", "price", "status", "valor_justo", "dy"])
            
            for item in avaliados:
                # Extraímos o DY do item (se não existir, salva 0)
                dy_valor = item.get("dy", 0)
                
                writer.writerow([
                    data_hoje,
                    item["ticker"],
                    item["score"],
                    item["price"], # Salvando apenas o número para facilitar cálculos futuros
                    item["status"],
                    item["valor_justo"], # Salvando apenas o número
                    dy_valor
                ])
        print(f"📈 Snapshot de hoje salvo em {path}")