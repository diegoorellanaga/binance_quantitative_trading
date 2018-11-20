#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 11:37:52 2018

@author: root
"""
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas_datareader.data as web
import datetime
#
import fix_yahoo_finance as fyf 
from pandas_datareader import data as pdr

fyf.pdr_override()

#start = datetime.datetime(2015, 1, 1)
#end = datetime.datetime.now()
##end = datetime.datetime(2017, 2, 1)
#stock='TSLA'  #GOO

#try:
#    df = pdr.get_data_yahoo(stock,start=start,end=end)
#    df.to_pickle('tsla.pkl')
#except:
#    df = pd.read_pickle('tsla.pkl')
#
#print(df.head())











app = dash.Dash()



app.layout = html.Div(children=[
        html.Div(children='''
                 Symbol to graph    
        '''),
 
        dcc.Input(id='input', value = '',type='text'),
        html.Div(id='output-graph'),     
        ])

@app.callback(
        Output(component_id='output-graph',component_property='children'),
        [Input(component_id='input',component_property='value')]
        )
def update_graph(input_data):
  #  input_data = 'TSLA'
    start = datetime.datetime(2015, 1, 1)
    end = datetime.datetime.now()
    try:
        df = pdr.get_data_yahoo(input_data,start=start,end=end)
        df.to_pickle('{0}.pkl'.format(input_data))
    except:
        df = pdr.read_pickle('tsla.pkl')   
        
    return dcc.Graph(
                id='example',
                figure={
                      'data':[
                              {'x':df.index,'y':df.Close.values,'type':'line','name':input_data},                   
                             ],
                              'layout': {
                                      'title': input_data
                                      }
                              
                          })
        
        
    
    
    
    
    
#    try:
#        return str(float(input_data)**2)
#    except:
#        return "some error"
#
#
#
#app.layout = html.Div(children=[
#        html.H1('Dash tutorialssss'),
#        dcc.Graph(id='example',
#                  figure ={
#                      'data':[
#                              {'x':[1,2,3,4,5,7],'y':[5,3,5,3,6,1],'type':'line','name':'boats'},
#                              {'x':[1,2,3,4,5,7],'y':[3,3,1,3,5,1],'type':'bar','name':'cars'},                      
#                             ],
#                              'layout': {
#                                      'title': 'Basic Dash example'
#                                      }
#                              
#                          })
#        ])


if __name__ == '__main__':
    app.run_server(debug=True)