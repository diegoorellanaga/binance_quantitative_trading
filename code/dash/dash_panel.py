import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import datetime
import fix_yahoo_finance as fyf 
from pandas_datareader import data as pdr
from training.extract_data import InfluxdbDataExtraction
from training.train_model import TrainModel

import numpy as np
import pandas as pd


fyf.pdr_override()

app = dash.Dash()

app.layout = html.Div([
    html.Hr(),
    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        id='dropdown-1',    
        options=[
            {'label': 'close price', 'value': 'close'},
            {'label': 'volume', 'value': 'volume'},
            {'label': 'number of trades', 'value': 'number_of_trades'}
        ],
        value=['close'],
        multi=True
    ),
    html.Div(id='output'),
    html.Hr(),
    html.Button('Extract data',id='button-data'),
    html.H4(id='button-clicks-2'),
    dcc.Dropdown(
        id='dropdown-plot',
        options=[
            {'label': 'close price', 'value': 'close'},
            {'label': 'volume', 'value': 'volume'},
            {'label': 'number of trades', 'value': 'number_of_trades'}
        ],
        value='close'
    ),
    html.Button('plot data',id='button-3'),    
    html.Div(id='output-graph')  
])


data_test_1 = pd.DataFrame(data=np.zeros([200,2]),columns=['test_1','test_2'])

@app.callback(
    Output('output-graph', 'children'),
    [Input('button-3', 'n_clicks'),
     Input('dropdown-plot', 'value')
     ])
def plot_graph(n_clicks,value):
    global data_test_1
    if n_clicks > 0:
       
            
            
        return dcc.Graph(
                    id='example',
                    figure={
                          'data':[
                                  {'x':data_test_1.values[:,-1],'y':data_test_1[value].values,'type':'line','name':'input_data'},                   
                                 ],
                                  'layout': {
                                          'title': 'input_data'
                                          }
                                  
                              })


@app.callback(
    Output('button-clicks-2', 'children'),
    [Input('button-data', 'n_clicks'),
     Input('dropdown-1', 'value')   
     ])
def load_data(n_clicks,value):
    global data_test_1
    if n_clicks > 0 :
        tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
        data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = value, measurement ="minute_tick" )
        data_test_1.dropna()
       # data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = ["close"], measurement ="minute_tick" )

    
    return 'shape of data is:{}'.format(data_test_1.shape) + ",data columns names are: " + " | ".join(list(data_test_1.columns))    
    
    


if __name__ == '__main__':
    app.run_server(debug=True,port=8051)
    
    
    
    
    
    
#    
#import matplotlib.pyplot as plt    
#    
#    
#tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
#data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = ['close'], measurement ="minute_tick" )    
#plt.plot(data_test_1[:,0])   
    
    