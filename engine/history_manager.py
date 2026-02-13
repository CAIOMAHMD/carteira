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

            # Cabeçalho completo
            if not file_exists:
                writer.writerow([
                    "data",
                    "ticker",
                    "price",
                    "valor_justo",
                    "margem",
                    "score",
                    "status",
                    "dy",
                    "pvp",
                    "is_fii"
                ])

            for item in avaliados:
                writer.writerow([
                    data_hoje,
                    item.get("ticker"),
                    item.get("price"),
                    item.get("valor_justo"),
                    item.get("margem"),
                    item.get("score"),
                    item.get("status"),
                    item.get("dy"),
                    item.get("pvp"),
                    item.get("is_fii")
                ])

        print(f"📈 Snapshot de hoje salvo em {path}")
