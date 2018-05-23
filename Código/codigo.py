import pandas as pd 
import numpy as np
import plotly
import plotly.graph_objs as go
import plotly.tools as tls
import folium
import matplotlib.pyplot as plt

'''
Manipulação dos dados primários
'''
#Dados de qualidade dos poços monitorados
def ler_dados_poços():
    '''
    Leitura dos dados de qualidade por parâmero e organização da informação de cada poço em um dicionário
    '''
    xls= pd.ExcelFile('dados.xls')
    sheets = xls.sheet_names
    dic_df_dados = pd.read_excel(xls,sheet_name=None, header=1)
    
    dados_poços = {}
    
    parametros = ['STD','Cloreto','Sulfato','Cor','Turbidez','E. Coli','Coliformes totais','Nitrito','Nitrato','pH']
    
    for i,poço in enumerate(dic_df_dados['STD']['Pontos']):
        dados_poços[poço] = {}
        for param in parametros:
            dados_poços[poço][param] = dic_df_dados[param].loc[i,'Janeiro':'Fevereiro']
    return dados_poços

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

#Classificar a água dos poços conforme CONAMA 396/2008 e Portaria do MS 518/2004:
def classif_agua(stats, dados_poços):
    df_poços = pd.DataFrame(dados_poços, columns=list(dados_poços.keys()))
    df_padrões = pd.read_excel('padrões de qualidade.xlsx',0,header=1,index_col=0)
    df_vrq = pd.read_excel('VRQ - poços.xlsx',0,header=1, index_col=0)

    VMPr_mais = {}
    VMPr_menos = {}
    for param in list(df_padrões.columns):
        '''
        Encontrar, entre os padrões de qualidade, o valor máximo permitido mais restritivo (VMPr+)
        e o menos restritivo (VMPr-)
        '''
        VMPr_mais[param] = float(df_padrões[param].min())
        VMPr_menos[param] = float(df_padrões[param].max())

    classes_poços = {}
    #Fazer análise do parâmetro para classificar:
    for poço in list(df_poços.columns): 
        if stats[poço]['Coliformes totais']['3º quartil'] > df_vrq['Coliformes totais'][poço] or (stats[poço]['Nitrato']['3º quartil'] > df_vrq['Nitrato'][poço] and stats[poço]['Nitrato']['3º quartil'] > 10):
            for param in list(df_poços[poço].index):
                if df_vrq[param][poço] < VMPr_mais[param] and stats[poço][param]['3º quartil'] <= df_vrq[param][poço]:
                    classes_poços[poço] = 'Classe 3'
                elif df_vrq[param][poço] < VMPr_menos[param] and stats[poço][param]['3º quartil'] <= df_vrq[param][poço]:
                    classes_poços[poço] = 'Classe 4'
                    break
        else:
            for param in list(df_poços[poço].index):
                if  stats[poço][param]['3º quartil'] <= VMPr_mais[param]:
                    if df_vrq[param][poço] <= VMPr_mais[param]:
                        classes_poços[poço] = 'Classe 1'
                    else:
                        classes_poços[poço] = 'Classe 2'
                        break 
    return(classes_poços, VMPr_mais)

#Quantidade de parâmetros que superam o VMPr+ por mês
def supera_mais_r(classes_poços,dados_poços, v_mais):
    poços = [poço for poço in list(classes_poços.keys()) if classes_poços[poço] != 'Classe 1']
    supera = {}
    for poço in poços:
        supera[poço] = {}
        for mês in list(dados_poços['P1']['pH'].keys()):
            supera[poço][mês] = {'Quantidade':0, 'Parâmetros':[]}
            for param in list(dados_poços[poço].keys()):
                if dados_poços[poço][param][mês] > v_mais[param]:
                    supera[poço][mês]['Quantidade'] += 1
                    supera[poço][mês]['Parâmetros'].append(param)
    return(supera)

#Gráfico polar com a quantidade de parâmetros que superam o VMPr+
def grafico_polar(supera, poço):
    mes_ano = []
    for mês in list(supera[poço].keys()):
        if mês == 'Fevereiro':
            mes_ano.append('Fevereiro/2010')
        else:
            mes_ano.append('{}/2009'.format(mês))
    quant = []
    for mês in list(supera[poço]):
        quant.append(list(supera[poço][mês].values())[0])
    params = []
    for mês in list(supera[poço]):
        params.append('Parâmetros: {}'.format(', '.join(list(supera[poço][mês].values())[1])))
    data = [
        go.Scatterpolar(
            #r = list(supera[poço].values()),
            r = quant,
            theta = mes_ano,
            text = params,
            mode = 'markers',
            marker = dict(
                color = '#00BFFF',
                size = 8
            )
        )
    ]
    layout = go.Layout(showlegend = False)
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename = '{}.html'.format(poço))

def map_whells(df_coordenadas,classes,dados_poços):
    
    #print(list(df_coordenadas['Poço']))
    m=folium.Map(location=[df_coordenadas['Latitude'][0] ,df_coordenadas['Longitude'][0]],zoom_start=12)
    #list(df_coordenadas['Poço'])
    labels = df_coordenadas['Poço'].values.tolist()
    #for i,poço in enumerate(labels):
    for i in range(len(df_coordenadas['Longitude'])):
        for poço in classes.keys():
       #popup=folium.Popup(labels[i], parse_html=True)
           html_info = """
           <h5> <b>Dados do Posto</b></h5>
           <p> <big><b>Nome: </b>{}</big><\p>
           <p> </big><b>Classe: </b> {} </big><\p>
           <p> </big><b>Latitude: </b>{} </big><\p>
           <p> </big><b>Longitude: </b> {} </big><\p>
           """.format(
           labels[i],
           classes[poço], 
           df_coordenadas['Latitude'][i],
           df_coordenadas['Longitude'][i]
           )
           folium.Marker([df_coordenadas['Latitude'][i],df_coordenadas['Longitude'][i]],
                          popup=html_info
                          ).add_to(m)
    
    m.save('index.html')


def gerar_boxplot(dados):
    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)
    ax.boxplot(dados)
    ax.set_xlabel('pH')
    plotly_fig = tls.mpl_to_plotly( mpl_fig )
    plotly.offline.plot(plotly_fig, filename='boxplot-basic.html')


dados_poços = ler_dados_poços()
stats = calc_stats(dados_poços)
df_coordenadas=manipular_coordenadas()
classes, v_mais = classif_agua(stats, dados_poços)
map_whells(df_coordenadas,classes,dados_poços)
supera = supera_mais_r(classes,dados_poços, v_mais)
for poço in list(supera.keys()):
    grafico_polar(supera, poço)