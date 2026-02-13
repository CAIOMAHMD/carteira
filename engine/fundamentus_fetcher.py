import pandas as pd
import requests
from io import StringIO
import numpy as np
import time

# ============================================================
#   AÇÕES - Fundamentus
# ============================================================

def obter_dados_b3():
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        df = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return pd.DataFrame()

    # Limpeza de colunas
    df.columns = [str(col).strip().replace('\n', '').replace('\r', '') for col in df.columns]

    # Mapeamento
    colunas_map = {
        'Cotação': 'price',
        'P/L': 'pl',
        'P/VP': 'pvp',
        'Div.Yield': 'dy',
        'LPA': 'lpa',
        'VPA': 'vpa',
        'Liq.2meses': 'liquidez'
    }
    df = df.rename(columns=colunas_map)

    # Blindagem
    cols_finais = ['price', 'pl', 'pvp', 'dy', 'lpa', 'vpa', 'liquidez']
    for col in cols_finais:
        if col not in df.columns:
            df[col] = 0.0

    # Conversão numérica
    for col in cols_finais:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = df[col].str.replace('.', '', regex=False)
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # DY decimal
    df['dy_dec'] = df['dy'] / 100
    df['dpa'] = df['price'] * df['dy_dec']

    # Bazin
    df['bazin_6'] = df['dpa'] / 0.06
    df['bazin_9'] = df['dpa'] / 0.09
    df['bazin_10'] = df['dpa'] / 0.10

    # Graham
    df['graham'] = np.sqrt(np.maximum(0, 22.5 * df['lpa'] * df['vpa']))

    # Classificação
    def classificar(row):
        if row['pvp'] <= 0.90 and row['dy'] >= 9:
            return "🔥 FORTE COMPRA"
        elif row['pvp'] <= 0.95 and row['dy'] >= 8:
            return "✅ COMPRA"
        else:
            return "⏳ AGUARDAR"

    df['status_estrategia'] = df.apply(classificar, axis=1)

    # Filtro de liquidez
    return df[df['liquidez'] > 1000000].copy()


# ============================================================
#   FIIs - Fundamentus
# ============================================================

def obter_dados_fii():
    url = "https://www.fundamentus.com.br/fii_resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        df = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]
    except Exception as e:
        print(f"❌ Erro na conexão FII: {e}")
        return pd.DataFrame()

    df.columns = [col.strip() for col in df.columns]

    colunas_map = {
        'Cotação': 'price',
        'Dividend Yield': 'dy',
        'P/VP': 'pvp',
        'Liquidez': 'liquidez',
        'Segmento': 'segmento',
        'Vacância Média': 'vacancia'
    }

    # Conversão numérica
    for col in df.columns:
        if col not in ['Papel', 'Segmento']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                val = df[col].astype(str).str.replace('%', '', regex=False)
                val = val.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(val, errors='coerce')

    df = df.rename(columns=colunas_map)

    # Criar colunas faltantes
    if 'lpa' not in df.columns: df['lpa'] = 0
    if 'vpa' not in df.columns: df['vpa'] = df['price'] / df['pvp']
    if 'roe' not in df.columns: df['roe'] = 0

    df['is_fii'] = True

    return df[df['liquidez'] > 500000].copy()
