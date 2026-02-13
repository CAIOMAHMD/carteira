import os
import sys
from process import processar_e_salvar_investimentos
from fetcher import DataFetcher
from score import ScoreEngine
from exporter import Exporter
from history_manager import HistoryManager
from investment_engine import InvestmentEngine
from analyzer import PortfolioAnalyzer

def formatar_valor_input(texto):
    if not texto:
        return 0.0
    limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(limpo)
    except ValueError:
        return None

def run():
    print("="*50)
    print("🚀 MATRIX INVEST ANALYZER PRO v.2026")
    print("Foco: Crescimento & Aposentadoria aos 50 Anos")
    print("="*50)
    
    # 1. Processamento de Planilhas
    processar_e_salvar_investimentos()
    
    # 2. Captura de Dados
    dados = DataFetcher.get_local_data()
    if not dados:
        print("❌ Falha ao carregar dados em 'data/'.")
        return

    # 3. Motor de Score e Valuation
    avaliados = [ScoreEngine.evaluate(d) for d in dados]
    
    # 4. Salvar Histórico (Snapshot)
    HistoryManager.save_snapshot(avaliados)
    
    # 5. Entrada de Aporte
    print("\n" + "—"*40)
    entrada = input("💰 Quanto temos para aporte/reinvestimento hoje? R$ ")
    valor_aporte = formatar_valor_input(entrada)
    
    if valor_aporte is None:
        print("⚠️ Valor inválido. Usando R$ 0.00")
        valor_aporte = 0.0
    
    # 6. Cálculo Oportunista com Arremate
    engine = InvestmentEngine(modo="moderado")
    sugestao_aporte = engine.calculate_allocation(avaliados, valor_aporte)

    
    # 7. Exportação e Análise de Tendência
    acoes = [a for a in avaliados if not a["is_fii"]]
    fiis = [f for f in avaliados if f["is_fii"]]
    
    # O Exporter já chama o PortfolioAnalyzer internamente agora
    Exporter.export_html(acoes, fiis, "exports/dashboard.html", sugestao_aporte)
    
    print("\n✅ Ciclo concluído com sucesso!")
    print(f"📊 Dashboard atualizado: exports/dashboard.html")
    
    # 8. Log de Tendência Rápido no Terminal
    resumo = PortfolioAnalyzer.get_trend_data()
    if resumo:
        print(f"\n📈 EVOLUÇÃO DA CARTEIRA:")
        print(f"⭐ Score: {resumo['score_atual']:.1f} ({resumo['score_delta']:+.1f}%)")
        print(f"💸 DY Médio: {resumo['dy_atual']:.2f}% ({resumo['dy_delta']:+.1f}%)")
    else:
        print("\nℹ️ Histórico iniciado. Tendências aparecerão a partir do próximo aporte.")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
        sys.exit()