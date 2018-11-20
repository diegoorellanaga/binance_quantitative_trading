# Import Supporting Libraries
import pandas as pd

# Import Dash Visualization Libraries
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import dash.dependencies
from dash.dependencies import Input, Output, State
import plotly


# Load datasets
US_STATES_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv'
US_AG_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv'
df_st = pd.read_csv(US_STATES_URL)
df_ag = pd.read_csv(US_AG_URL)
print(df_st.head())
print(df_ag.head())


# Create our app layout
app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H2('My Dash App'),
    dt.DataTable(
        id='my-datatable',
        rows=df_ag.to_dict('records'),
        editable=False,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[]
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='datatable-subplots'
    ),
    # +++++++++ START UPDATED APP LAYOUT FOR QUERY BUTTON ++++++++++
    html.Div([
        html.Div(id='container-query-button', children=[
            html.Button('Run Query', id='button-query', disabled=True),
        ]),
        dcc.Textarea(
            id='textbox-population',
            placeholder='Select a single row to query in the datatable',
            value=None,
            style={'width': '40%'}
        ),
        html.Br([])
    ], className='container'),
    # +++++++++ END UPDATED APP LAYOUT FOR QUERY BUTTON ++++++++++
], style={'width': '60%'})
    
'''   

# Create our app layout
app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.H2('My Dash App'),
    dt.DataTable(
        id='my-datatable',
        rows=df_ag.to_dict('records'),
        editable=False,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[]
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='datatable-subplots'
    )
], style={'width': '60%'})
    
'''    
    
    

@app.callback(Output('my-datatable', 'selected_row_indices'),
              [Input('datatable-subplots', 'clickData')],
              [State('my-datatable', 'selected_row_indices')])
def updated_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices    
    
    
    
    
    
@app.callback(Output('datatable-subplots', 'figure'),
              [Input('my-datatable', 'rows'),
               Input('my-datatable', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=3, cols=1,
        subplot_titles=('Beef', 'Pork', 'Poultry'),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['state'],
        'y': dff['beef'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['state'],
        'y': dff['pork'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    fig.append_trace({
        'x': dff['state'],
        'y': dff['poultry'],
        'type': 'bar',
        'marker': marker
    }, 3, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 1000
    fig['layout']['width'] = 1200
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    return fig







@app.callback(Output('button-query', 'disabled'),
              [Input('my-datatable', 'selected_row_indices')])
def show_hide_query_button(selected_row_indices):
    """ Callback enables/disables the query button depending on the number of rows selected. """
    if len(selected_row_indices) == 1:
        return False
    else:
        return True


@app.callback(Output('textbox-population', 'value'),
              [Input('button-query', 'n_clicks'),
               Input('my-datatable', 'selected_row_indices'),
               Input('my-datatable', 'rows')])
def query_button_clicked(n_clicks, selected_row_indices, rows):
    """ Callback to retrieve the state population and output to the textbox. """
    if n_clicks > 0 and len(selected_row_indices) == 1:
        row_idx = selected_row_indices[0]
        state = rows[row_idx]['state']
        population = df_st.loc[df_st['State'] == state, 'Population'].values
        print(population)
        value = 'Population of ' + state + ' is ' + str(population)
    else:
        n_clicks = 0
        value = 'Select a single row to query in the datatable'
    return value






app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(debug=True)    