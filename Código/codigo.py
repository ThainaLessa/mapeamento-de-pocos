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

#Coordenadas geográficas
#Transformar grau, minuto e segundo em grau decimal:
def dms_to_dd(d, m, s):
    dd = d + float(m)/60 + float(s)/3600
    return dd
def manipular_coordenadas():
    df = pd.read_excel('coordenadas.xlsx', 0, header=0, index_col=0)

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
#Cálculo das estatísticas do valor do 3º quartil para cada conjunto de dados
def calc_stats(dados_poços):
    df = pd.DataFrame(dados_poços, columns=list(dados_poços.keys()))

    stats = {}

    for poço in list(df.columns):
        stats[poço] = {}
        for param in list(df[poço].index):
            stats[poço][param] = {}
            #Trocar valor não numérico (string no nosso caso) por NaN para poder realizar os cálculos posteriormente:
            df[poço][param] = pd.to_numeric(df[poço][param], errors='coerce')
            
            #Cálculo do valor do 3º quartil:
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

#Quantidade de parâmetros que superam o VMPr+
def supera_mais_r(classes_poços,dados_poços, v_mais):
    '''
    Esta função analisa quais e quantos parâmetros monitorados de cada poço superaram o valor de 
    referência de qualidade para consumo humano (VMPr+), por mês e em todo o período analisado.
    '''
    poços = [poço for poço in list(classes_poços.keys()) if classes_poços[poço] != 'Classe 1']

    supera = {}

    for poço in poços:
        supera[poço] = {}
        supera[poço]['Superaram'] = []
        
        for mês in list(dados_poços['P1']['pH'].keys()):
            supera[poço][mês] = {'Quantidade':0, 'Parâmetros':[]}
            for param in list(dados_poços[poço].keys()):
                if dados_poços[poço][param][mês] > v_mais[param]:
                    supera[poço][mês]['Quantidade'] += 1
                    supera[poço][mês]['Parâmetros'].append(param)
                    if param not in supera[poço]['Superaram']:
                        supera[poço]['Superaram'].append(param)

        #Exluir chave (poço) em que nenhum parâmetro ficou fora do padrão:
        if bool(supera[poço]) == False:
            del supera[poço]
    return(supera)

#Gráfico polar com a quantidade de parâmetros que superam o VMPr+
def grafico_polar(supera, poço):
    '''
    Esta função cria um gráfico polar que informa a quantidade de parâmetros monitorados 
    que superaram o valor de referência para consumo humano, por mês, do poço.
    '''
    meses = [mês for mês in list(supera[poço].keys()) if mês != 'Superaram']

    #Renomear nome do mês para ter também o ano de monitoramento:
    mes_ano = []
    for mês in meses:
        if mês == 'Fevereiro':
            mes_ano.append('Fevereiro/2010')
        else:
            mes_ano.append('{}/2009'.format(mês))

    #Salvar quantidade de parâmetros fora dos padrões, por mês, em uma lista:
    quant = []
    for mês in meses:
        quant.append(supera[poço][mês]['Quantidade'])

    #Salvar nomes dos parâmetros fora dos padrões, por mês, em uma lista:
    params = []
    for mês in meses:
        params.append('Parâmetros: {}'.format(', '.join(list(supera[poço][mês].values())[1])))
    
    #Gráfico polar:
    data = [
        go.Scatterpolar(
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
    layout = go.Layout(showlegend = False, 
        title = 'Poço {} - Quantidade de parâmetros de qualidade da água que superaram o valor de referência para consumo humano'.format(poço))
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename = 'polar_{}.html'.format(poço), auto_open=False)

def map_whells(df_coordenadas,classes,dados_poços,supera):
    '''
    Esta função gera o mapa com a localização e informações dos poços monitorados.
    '''
    #Criação do mapa passando as coordenadas do poço P6, por ser um poço central, apenas para melhor visualização ao inserir os demais:
    mapa = folium.Map(location=[df_coordenadas['Latitude']['P6'] ,df_coordenadas['Longitude']['P6']],zoom_start=12)
    
    for poço in classes.keys():
        #Informações a serem apresentadas ao clicar nos poços em um pop-up:    
        html_info = """
        <h5> <b>Dados do Posto</b></h5>
        <p><big><b> Nome: </b>{}</big><\p>
        <p><big><b> Classe: </b>{}</big><\p>
        <p><big><b> Latitude: </b>{}</big><\p>
        <p><big><b> Longitude: </b>{}</big><\p>
        <p><b> Parâmetros fora dos padrões para consumo humando: </b></p>
        <p><a href="{}", target = blank > Gráfico polar </a></p>
        <p>Gráficos boxplot:</p>
        """.format(
        poço,
        classes[poço], 
        df_coordenadas['Latitude'][poço],
        df_coordenadas['Longitude'][poço],
        'polar_{}.html'.format(poço)
        )
        for param in supera[poço]['Superaram']:
            html_info += '<a href="boxplot_{}_{}.html", target = blank > {} </a>'.format(param,poço,param)
        html_info += '<p>Dados de monitoramento:</p>'
        for param in supera[poço]['Superaram']:
            html_info += '<a href="temporal_{}_{}.html", target = blank > {} </a>'.format(param,poço,param)
        
        #Inserir poço no mapa:
        cores = {'Classe 1':'lightblue','Classe 2':'blue','Classe 3':'lightgray','Classe 4':'gray'}
        folium.Marker([df_coordenadas['Latitude'][poço],df_coordenadas['Longitude'][poço]],popup=html_info,
        icon=folium.Icon(color=cores[classes[poço]])).add_to(mapa)
    
    mapa.save('index.html')

def boxplots(dados_poços, supera, poço):
    '''
    Esta função gera um gráfico boxplot para cada conjunto de parâmetros do poço que ficou fora 
    dos padrões.
    '''
    for param in supera[poço]['Superaram']:
        dados = [go.Box(
            y=list(dados_poços[poço][param]),
            name = param
            )]
        fig = go.Figure(data=dados)
        plotly.offline.plot(fig, filename='boxplot_{}_{}.html'.format(param,poço), auto_open=False)
        
def graficos_temp(dados_poços, supera, poço):
    '''
    Esta função gera um gráfico para cada conjunto de parâmetros do poço, no tempo, 
    que ficou fora dos padrões.
    '''
    for param in supera[poço]['Superaram']:
        dados = [go.Scatter(
            x = list(dados_poços[poço][param].keys()),
            y = list(dados_poços[poço][param]),
            mode = 'markers',
            marker = dict(
                color = '#00BFFF',
                size = 10))]
        layout = go.Layout(showlegend = False, 
        title = 'Poço {} - {}: Dados de monitoramento de janeiro de 2009 a fevereiro de 2010'.format(poço,param))
        fig = go.Figure(data=dados,layout=layout)
        plotly.offline.plot(fig, filename='temporal_{}_{}.html'.format(param,poço), auto_open=False)


dados_poços = ler_dados_poços()
stats = calc_stats(dados_poços)
df_coordenadas=manipular_coordenadas()
classes, v_mais = classif_agua(stats, dados_poços)
map_whells(df_coordenadas,classes,dados_poços)
supera = supera_mais_r(classes,dados_poços, v_mais)
for poço in list(supera.keys()):
    grafico_polar(supera, poço)