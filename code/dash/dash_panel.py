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
    html.Label('Select coin-pair to extract'),
    dcc.Dropdown(
        id='dropdown-coin',    
        options=[
            {'label': 'IOTA-USTD', 'value': 'IOTAUSDT'},
            {'label': 'BITCOIN-USTD', 'value': 'BTCUSDT'},
            {'label': 'RIPPLE-USTD', 'value': 'XRPUSDT'}
        ],
        value='IOTAUSTD',
    ),    
    
    
    
    html.Label('Select data to extract'),
    dcc.Dropdown(
        id='dropdown-fields',    
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
    html.P(id='train-data'),    
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
    html.Div(id='output-graph'),
    
    html.Label('Past Units '),
    dcc.Input(
    id='input_0',
    placeholder=14,
    type='number',
    value=14
              ),    
    html.Label('Future Units '),
    dcc.Input(
    id='input_1',         
    placeholder=5,
    type='number',
    value=5
              ),  
    html.Label('Number of Features '),
    dcc.Input(
    id='input_2',         
    placeholder=2,
    type='number',
    value=1
              ),              
    html.Label('Position Feature '),
    dcc.Input(
    id='input_3',         
    placeholder=0,
    type='number',
    value=0
              ),      
    html.Label('Hidden Neurons '),
    dcc.Input(
    id='input_4',         
    placeholder=70,
    type='number',
    value=70
              ),   
    html.Label('Epoch '),
    dcc.Input(
    id='input_5',         
    placeholder=20,
    type='number',
    value=2
              ),              
    html.Label('Batch Size '),
    dcc.Input(
    id='input_6',         
    placeholder=72,
    type='number',
    value=72
              ),              
    html.Label('Dropout yes/no = 1/0 '),
    dcc.Input(
    id='input_7',         
    placeholder=1,
    type='number',
    value=1
              ),     
    html.Label('Name of Model to Save '),
    dcc.Input(
    id='input_8',         
    placeholder='Model_1',
    type='text',
    value='Model_1'
              ),              
    html.Button('Train Model',id='button-train'),    
    
    html.Div(id='output-graph-train'),    
    
    
    
    
    
    
    
])


data_test_1 = pd.DataFrame(data=np.zeros([200,2]),columns=['test_1','test_2'])

@app.callback(
    Output('output-graph', 'children'),
    [Input('button-3', 'n_clicks'),
     Input('dropdown-plot', 'value'),
     Input('dropdown-coin', 'value')
     ])
def plot_graph(n_clicks,value,value_coin):
    global data_test_1
    if n_clicks > 0:
       
            
            
        return dcc.Graph(
                    id='example',
                    figure={
                          'data':[
                                  {'x':data_test_1.values[:,-1],'y':data_test_1[value].values,'type':'line','name':'input_data'},                   
                                 ],
                                  'layout': {
                                          'title': value_coin
                                          }
                                  
                              })


@app.callback(
    Output('button-clicks-2', 'children'),
    [Input('button-data', 'n_clicks'),
     Input('dropdown-fields', 'value'),
     Input('dropdown-coin', 'value') 
     ])
def load_data(n_clicks,value,value_coin):
    global data_test_1
    if n_clicks > 0 :
        tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
        data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = value_coin, unit = "1h",data_to_extract = value, measurement ="minute_tick" )
        data_test_1.dropna()
       # data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = "BTCUSDT", unit = "1h",data_to_extract = ["close"], measurement ="minute_tick" )

    
    return 'shape of data is: {}'.format(data_test_1.shape) + ", data columns names are: " + " | ".join(list(data_test_1.columns))    
    



@app.callback(
    Output('output-graph-train', 'children'),
    [Input('button-train', 'n_clicks'),
     Input('input_0', 'value'), #past
     Input('input_1', 'value'), #future
     Input('input_2', 'value'), #num features
     Input('input_3', 'value'), #position feature
     Input('input_4', 'value'), # hidden
     Input('input_5', 'value'), # epoch
     Input('input_6', 'value'), # batch
     Input('input_7', 'value'),  # drop
     Input('input_8', 'value')  # name of model     
     ])
def train_data(n_clicks,value_0,value_1,value_2,value_3,value_4,value_5,value_6,value_7,value_8):
    global data_test_1
    LSTM_1 = TrainModel(raw_data=data_test_1,name = "test_1",dataFrame= True)
    LSTM_1.create_data_frame(columns=LSTM_1.columns)
    LSTM_1.drop_nan_rows()
    LSTM_1.drop_column('time')
    LSTM_1.scale_data(tuple_limit = (0,1))
    LSTM_1.shift_data(past_units = int(value_0),future_units = int(value_1),num_features = int(value_2),position_feature = int(value_3))
    LSTM_1.split_data_train_test(0.8)
    LSTM_1.split_data_x_y(predict_present = True)
 #   print(n_clicks,value_0,value_1,value_2,value_3,value_4,value_5,value_6,value_7,value_8)
 #   LSTM_1.train_model_regression_LSTM(hidden_neurons=int(value_4),epochs=int(value_5),batch_size=int(value_6), dropout = int(value_7))
 #   LSTM_1.save_model(path_model="",path_weigths="",model_id=str(value_8))
    
    
    return dcc.Graph(
                    id='example-1',
                    figure={
                          'data':[
                                  {'x':list(range(100)),'y':list(range(100)),'type':'line','name':'loss'},                   
                                 ],
                                  'layout': {
                                          'title': 'loss'
                                          }
                                  
                              }) 













    


if __name__ == '__main__':
    app.run_server(debug=True,port=8055)
    
    
'''    
               {'label': 'IOTA-USTD', 'value': 'IOTAUSDT'},
            {'label': 'BITCOIN-USTD', 'value': 'BTCUSDT'},
            {'label': 'RIPPLE-USTD', 'value': 'XRPUSTD'} 
'''    
    
#    
#import matplotlib.pyplot as plt    
#    
##    
#tf_influxdb_1 = InfluxdbDataExtraction(host='localhost', port=8086,database="binance")
#data_test_1 =  tf_influxdb_1.extract_data_basic(coin_id = "XRPUSTD", unit = "1h",data_to_extract = ['close'], measurement ="minute_tick" )    
#plt.plot(data_test_1[:,0])   
#LSTM_1 = TrainModel(raw_data=data_basic,name = "test_1",dataFrame= True)
#LSTM_1.create_data_frame(columns=LSTM_1.columns)
#LSTM_1.drop_nan_rows()
#LSTM_1
##LSTM_1.diff_data()
##LSTM_1.drop_nan_rows()
#LSTM_1.drop_column('time')
#LSTM_1.scale_data(tuple_limit = (0,1))
#LSTM_1.shift_data(past_units = 14,future_units = 5,num_features = 2,position_feature = 0)
#LSTM_1.split_data_train_test(0.8)
#LSTM_1.split_data_x_y(predict_present = True)
#LSTM_1.train_model_regression_LSTM(hidden_neurons=80,epochs=20,batch_size=72, dropout = True)
#LSTM_1.save_model(path_model="",path_weigths="",model_id="14-5-1-drop02-present_prediction_80-50-72_3")
##LSTM_1.load_model(path_model="",path_weigths="",model_id="drop_diff_4")
#LSTM_1.get_predicted_data()
#LSTM_1.invert_scale_prediction()
#LSTM_1.plotPredictedOriginal()
##pyplot.plot(LSTM_1.df_data.values[:,0])
##LSTM_1.df_data.shape    
    