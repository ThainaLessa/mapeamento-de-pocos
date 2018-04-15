# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 11:36:23 2018

@author: victo
"""

import pandas as pd

def read_xls():
    xls= pd.ExcelFile('dados.xls')
    sheets = xls.sheet_names
    dic_df_dados = pd.read_excel(xls,sheet_name=None, header=1)
    
    '''
    return(sheets)'''
    
    '''
    return dic_df_dados'''
    
    #retornando um dos dataframes
    '''
    return(dic_df_dados['Nitrato'])'''
    
    #retornado uma coluna
    '''
    return(dic_df_dados['Nitrato']['Pontos'])'''
    
    #retornando uma linha do dataframe
    '''
    a=dic_df_dados['Nitrato']
    return(a.loc[14])'''
    #teste de repetição para acessar dataframe
    '''
    b=0
    
    for i in range(0,14):
        a=dic_df_dados['Nitrato']
        return(a.loc[b])
        b=b+1
    '''
    #talvez de pra dar split, aplicando metodos de string em dataframe(pandas dá essa possibilidade)
    '''
    a=dic_df_dados['Nitrato']
    b=a.str.split(",")
    print(b)'''
    #erro AttributeError: 'DataFrame' object has no attribute 'str', no entanto na documentação há esse método
   
    #usando repetição no iloc só retorna uma Series, não repete o return
    
    #tentando mexer com listas, acho que é mais fácil aplicar seleção nelas
    
    '''
    v=[]
    a = dic_df_dados['Nitrato']
    for i in range (0,9):
        b=a.iloc[i]
        v.append(b)
        '''
      
    
read_xls()