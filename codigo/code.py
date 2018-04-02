'''
Bibliotecas necessárias para importação:
'''
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np

'''
Arquivos de entrada:
'''
dados = 'dados.xls'
portariaMS = 'Portaria.xls'
coordenadas = 'poços.xls'
'''
Leitura do arquivo de entrada dados.xls e portariaMS.xls:
'''
def read_xls(path1, path2):
    xls = pd.ExcelFile(path1)
    # Lista com nomes das planilhas existentes no arquivo:
    sheets = xls.sheet_names
    # Dicionário de DataFrames (para múltiplas planilhas):
    dic_df_dados = pd.read_excel(xls,sheet_name=None, header=1)

    df_portaria = pd.read_excel(path2, 0, header=0)

    return [sheets, dic_df_dados, df_portaria]

'''
Análise das séries e mudança de valores:
'''
def series_analyses(dic_df_dados, sheets):
    '''
    Serão alterados valores recebidos como asteriscos e hífens para troca por NaN
    e alteração das séries.
    '''
    return(dic_df_change)

'''
Cálculo dos valores mínimo, máximo, mediana e 3º quartil para cada série de parâmetro.
Serão criados DataFrames referentes a esses cálculos:
'''
def calc_stats(dic_df_change): 
    return [df_min, df_max, df_med, df_q3]

'''
Comparação do 3º quartil com o valor de referência estabelecido pela Portaria do MS
para análise da potabilidade. Será criado um DataFrame indicando a situação de cada 
parâmetro por poço, com DENTRO ou FORA, para dentro e fora dos padrões:
'''
def comp_ref(df_q3, df_portaria):
    return df_situation

# Para definição de como será o enquadramento falta conversar com a professora

'''
    Gráfico do comportamento do parâmetro no tempo.
'''
def graph_temp(dic_df_change, df_portaria):
    
def map_quality(df_situation, df_coord):
    #plotly, bokeh... (?)