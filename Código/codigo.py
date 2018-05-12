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
    
    dados_poços = {}
    
    parametros = ['STD','Cloreto','Sulfato','Cor','Turb','E. Coli','Coliformes totais','Nitrato','Nitrito','pH']
    
    for i,poço in enumerate(dic_df_dados['STD']['Pontos']):
        
        dados_poços[poço] = {}
        
        for num_param in parametros:
            
            dados_poços[poço][num_param] = dic_df_dados[num_param].loc[i,'Jan/Fev':'Fev']
    
    return dados_poços
#Coordenadas geográficas
#Transformar grau, minuto e segundo em grau decimal:
def dms_to_dd(d, m, s):
    dd = d + float(m)/60 + float(s)/3600
    return dd
def manipular_coordenadas():
    df = pd.read_excel('coordenadas.xlsx', 0, header=0)

    for i in range(len(df['Longitude'])):
        lat = df['Latitude'][i]
        lon = df['Longitude'][i]
        #Uniformizando a escrita das coordenadas:
        g_lat, m_lat, s_lat = lat.replace('°',' ').replace("''",'"').replace("'",' ').replace('"','').split(' ')
        g_lon, m_lon, s_lon = lon.replace('°',' ').replace("''",'"').replace("'",' ').replace('"','').split(' ')

        #Mudar de coordenadas geográficas grau, minuto, segundo para grau decimal (*(-1) para representar Sul e Oeste):
        df['Latitude'][i] = dms_to_dd(int(g_lat),int(m_lat),float(s_lat))*(-1)
        df['Longitude'][i] = dms_to_dd(int(g_lon),int(m_lon),float(s_lon))*(-1)
    return(df)

'''
Cálculos e análises
'''
#Cálculo das estatísticas: mínimo, máximo, média, mediana e 3º quartil:
def calc_stats(dados_poços):
    df = pd.DataFrame(dados_poços, columns=list(dados_poços.keys()))
    stats = {}

    for poço in list(df.columns):
        stats[poço] = {}
        for param in list(df[poço].index):
            stats[poço][param] = {}
            #Trocar valor não numérico (string no nosso caso) por NaN para poder realizar os cálculos posteriormente:
            df[poço][param] = pd.to_numeric(df[poço][param], errors='coerce')
            
            #Cálculo das estatísticas:
            stats[poço][param]['Máximo'] = df[poço][param].drop(df[poço][param].index[0]).max()
            stats[poço][param]['Mínimo'] = df[poço][param].drop(df[poço][param].index[0]).min()
            stats[poço][param]['Média'] = df[poço][param].drop(df[poço][param].index[0]).mean()
            stats[poço][param]['Mediana'] = df[poço][param].drop(df[poço][param].index[0]).median()
            stats[poço][param]['3º quartil'] = df[poço][param].drop(df[poço][param].index[0]).sort_values().quantile(q=0.75, interpolation='midpoint')
    return stats

#Classificar a água dos poços conforme CONAMA 396/2008 e Porria do MS 518/2004:
def classif_agua(stats, dados_poços):
    df_poços = pd.DataFrame(dados_poços, columns=list(dados_poços.keys()))
    df_padrões = pd.read_excel('padrões de qualidade.xlsx',0,header=1,index_col=0)
    df_vrq = pd.read_excel('VRQ - poços.xlsx',0,header=1,index_col=0)

    VMPr_mais = {}
    VMPr_menos = {}
    for param in list(df_padrões.columns):
        '''
        Encontrar, entre os padrões de qualidade, o valor máximo permitido mais restritivo (VMPr+)
        e o menos restritivo (VMPr-)
        '''
        VMPr_mais[param] = df_padrões[param].min()
        VMPr_menos[param] = df_padrões[param].max()
    
    #Fazer análise do parâmetro para classificar:
    '''
    VERIFICAR EXISTÊNCIA DE COLIFORMES E/OU NITRATO PARA CLASSIFICAR COMO CLASSE 3/4 
    Alterar --> Thainá 
    '''
    for poço in list(df_poços.columns):
        for param in list(df_poços[poço].index):
            if  stats[poço][param]['3º quartil'] <= VMPr_mais[param]:
                if df_vrq[param][poço] <= VMPr_mais[param]:
                    print(poço+param+'Classe 1')
                else:
                    print(poço+param+'Classe 2')
            else:
                if df_vrq[param][poço] > VMPr_mais[param] and stats[poço][param]['3º quartil'] <= df_vrq[param][poço]:
                    print(poço+param+'Classe 3')
                elif df_vrq[param][poço] > VMPr_menos[param] and stats[poço][param]['3º quartil'] <= df_vrq[param][poço]:
                    print(poço+param+'Classe 4')

'''
Criar banco de dados --> Thainá
'''

'''
Mapa --> Victor
'''
