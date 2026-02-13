import re
import csv
import os

def processar_e_salvar_investimentos():
    labels_acoes = [
        "Ticker", "Quant.", "Preço Médio", "Preço Atual", "Payout", "PL", "PVP", 
        "DY 12 Meses", "YOC", "ROE", "Margem Líquida", "Margem Bruta", 
        "CAGR Receitas", "CAGR Lucro"
    ]
    
    # NOVA ESTRUTURA DOS FIIs (16 CAMPOS)
    labels_fiis = [
        "Ticker", "Quant.", "PreçoAtual", "Variacao", "Rentabilidade",
        "ValorPatrimonialCota", "UltimoRendimento", "PatrimonioTotal",
        "NumeroCotistas", "CotasEmitidas", "Vacancia", "PVP",
        "DY12Meses", "YieldOnCost", "TIPO"
    ]

    def extrair_valores(caminho):
        if not os.path.exists(caminho):
            print(f"❌ Arquivo não encontrado: {caminho}")
            return []
        
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()

            # Remove R$, %, tabs e múltiplos espaços
            conteudo = conteudo.replace("R$", "").replace("%", "")
            conteudo = re.sub(r'\s+', ' ', conteudo)

            valores = [v.strip() for v in conteudo.split(" ") if v.strip()]
            return valores

    def salvar_csv(caminho_saida, labels, valores, tipo):
        tamanho_bloco = len(labels)
        total_valores = len(valores)

        if total_valores == 0:
            print(f"⚠️ Nenhum valor extraído para {tipo}.")
            return

        with open(caminho_saida, 'w', newline='', encoding='utf-8-sig') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerow(labels)

            contagem = 0
            for i in range(0, total_valores, tamanho_bloco):
                bloco = valores[i:i+tamanho_bloco]

                if len(bloco) == tamanho_bloco:
                    escritor.writerow(bloco)
                    contagem += 1
                else:
                    print(f"⚠️ Bloco incompleto em {tipo} (Ativo: {bloco[0] if bloco else 'desconhecido'}). "
                          f"Esperado {tamanho_bloco}, recebeu {len(bloco)}.")

            print(f"✅ {tipo}: {contagem} registros salvos em {caminho_saida}")

    # Execução
    if not os.path.exists('data'):
        os.makedirs('data')

    acoes_bruto = extrair_valores('data/acoes-dados-bruto.csv')
    salvar_csv('data/acoes.csv', labels_acoes, acoes_bruto, "Ações")

    fiis_bruto = extrair_valores('data/fiis-dados-bruto.csv')
    salvar_csv('data/fiis.csv', labels_fiis, fiis_bruto, "FIIs")

if __name__ == "__main__":
    processar_e_salvar_investimentos()
