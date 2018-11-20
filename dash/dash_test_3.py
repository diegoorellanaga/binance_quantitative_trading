import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import datetime
import fix_yahoo_finance as fyf 
from pandas_datareader import data as pdr
from training.extract_data import tensorflow_influxdb



fyf.pdr_override()

app = dash.Dash()

app.layout = html.Div([
    html.Button('Click Me', id='button'),
    html.H3(id='button-clicks'),

    html.Hr(),

    html.Label('Input 1'),
    dcc.Input(id='input-1'),

    html.Label('Input 2'),
    dcc.Input(id='input-2'),

    html.Label('Slider 1'),
    dcc.Slider(id='slider-1'),

    html.Button('Click Me 2',id='button-2'),

    html.Div(id='output'),
    html.Hr(),

    html.Button('Extract data',id='button-data'),
    html.H4(id='button-clicks-2'),

    html.Button('Click Me 3',id='button-3'),    
    html.Div(id='output-graph')
    
    
    
])

@app.callback(
    Output('output-graph', 'children'),
    [Input('button-3', 'n_clicks')])
def plot_graph(n_clicks):
    if n_clicks > 0:
        input_data = 'TSLA'
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


@app.callback(
    Output('button-clicks-2', 'children'),
    [Input('button-data', 'n_clicks')])
def load_data(n_clicks):
    
    if n_clicks > 0 :
        tf_influxdb_1 = tensorflow_influxdb(host='localhost', port=8086,database="binance", measurement="minute_tick")

        data_test_1 =  tf_influxdb_1.all_at_once(coin_id="IOTAUSDT",points_set_size=1,time_sets_to_consider=["minutes"],point_size=1*1*3,total_points=0,only_value=True,unit = 1,data_to_extract="LAST(close),LAST(volume),LAST(number_of_trades)")

    
    return 'shape of data is:{}'.format(data_test_1.shape)    
    
    

@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def clicks(n_clicks):
    return 'Button has been clicked {} times'.format(n_clicks)

@app.callback(
    Output('output', 'children'),
    [Input('button-2', 'n_clicks')],
    state=[State('input-1', 'value'),
           State('input-2', 'value'),
           State('slider-1', 'value')])
def compute(n_clicks, input1, input2, slider1):
    return 'A computation based off of {}, {}, and {}'.format(
        input1, input2, slider1
    )

if __name__ == '__main__':
    app.run_server(debug=True)
    
    