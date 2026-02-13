import pandas as pd
import os

def processar_e_salvar_investimentos():

    # Caminhos corretos dos arquivos gerados pelo AutoFetcher
    path_acoes = "data/acoes.csv"
    path_fiis = "data/fiis.csv"

    # Verifica existência
    if not os.path.exists(path_acoes):
        print("❌ Arquivo não encontrado: data/acoes.csv")
        acoes = pd.DataFrame()
    else:
        acoes = pd.read_csv(path_acoes, sep=";")

    if not os.path.exists(path_fiis):
        print("❌ Arquivo não encontrado: data/fiis.csv")
        fiis = pd.DataFrame()
    else:
        fiis = pd.read_csv(path_fiis, sep=";")

    # Se ambos vazios, nada a fazer
    if acoes.empty and fiis.empty:
        print("⚠️ Nenhum valor extraído para Ações ou FIIs.")
        return

    # Salva arquivos processados (mantém o padrão do pipeline)
    acoes.to_csv("data/acoes-processado.csv", sep=";", index=False)
    fiis.to_csv("data/fiis-processado.csv", sep=";", index=False)

    print("📁 Dados processados e salvos com sucesso!")
