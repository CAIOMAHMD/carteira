import pandas as pd
import os

class PortfolioAnalyzer:
    @staticmethod
    def get_trend_data(history_path="data/historico.csv"):
        if not os.path.exists(history_path):
            return None

        try:
            # Lê o CSV detectando o separador ";" e ignorando o cabeçalho se necessário
            df = pd.read_csv(history_path, sep=";", engine='python', on_bad_lines='skip')
            
            if df.empty:
                return None

            # Normaliza nomes de colunas para minúsculo
            df.columns = [c.strip().lower() for c in df.columns]
            
            # Garante que as colunas essenciais existem
            if 'data' not in df.columns or 'score' not in df.columns:
                return None

            # Converte a data e remove a hora para agrupar por dia
            df['data'] = pd.to_datetime(df['data']).dt.date
            
            # Agrupa por dia para calcular a média da carteira
            # Se não houver coluna 'dy', ele usa apenas o 'score'
            agg_dict = {'score': 'mean'}
            if 'dy' in df.columns:
                agg_dict['dy'] = 'mean'
                
            tendencia = df.groupby('data').agg(agg_dict).sort_index()

            # Se só houver registros de 1 dia, não há o que comparar ainda
            if len(tendencia) < 2:
                return None

            atual = tendencia.iloc[-1]
            anterior = tendencia.iloc[-2]
            
            # Cálculo dos deltas
            score_delta = ((atual['score'] / anterior['score']) - 1) * 100 if anterior['score'] > 0 else 0
            
            dy_atual = atual.get('dy', 0)
            dy_anterior = anterior.get('dy', 0)
            dy_delta = ((dy_atual / dy_anterior) - 1) * 100 if dy_anterior > 0 else 0
            
            return {
                "score_atual": atual['score'],
                "score_delta": score_delta,
                "dy_atual": dy_atual,
                "dy_delta": dy_delta
            }
        except Exception as e:
            # Silencioso no Dash, mas avisa o desenvolvedor se algo bizarro ocorrer
            print(f"ℹ️ Analisador aguardando evolução temporal: {e}")
            return None