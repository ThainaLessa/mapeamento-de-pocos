import pandas as pd 
import numpy as np

'''
Manipulação dos dados primários
'''
#Dados de qualidade dos poços monitorados
def ler_dados_poços(arq_xls):
    '''
    Leitura dos dados de qualidade por parâmero e organização da informação de cada poço em um dicionário
    '''
    xls= pd.ExcelFile('dados.xls')
    sheets = xls.sheet_names
    dic_df_dados = pd.read_excel(xls,sheet_name=None, header=1)
   
    #Completar --> Victor
   
    return dados_poços
#Coordenadas geográficas
#Transformar grau, minuto e segundo em grau decimal:
def dms_to_dd(d, m, s):
    dd = d + float(m)/60 + float(s)/3600
    return dd
def manipular_coordenadas():
    

'''
Cálculos e análises
'''
#Cálculo das estatísticas: mínimo, máximo, média, mediana e 3º quartil:
def calc_stats(dados_poços):
    

#Classificar a água dos poços conforme CONAMA 396/2008 e Porria do MS 518/2004:
def classif_agua(stats, dados_poços):

'''
Criar banco de dados --> Thainá
'''

'''
Mapa --> Victor
'''