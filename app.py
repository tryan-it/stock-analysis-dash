# Import of Necessary Libraries
from re import template
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import alpaca_trade_api as tradeapi

# -- Dash Components
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# -- Dash HTML Elements
from dash.html import Nav
from dash.html import Ul
from dash.html import Div
# -- Dash Additional Libraries
import dash_bootstrap_components as dbc

# Config and Class Imports
from config import *
from stockdata import StockData
from stockcorr import StockCorr


  

# Define Dash App Configurations
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions = True)
title = 'Stock Analysis'
nasdaq = pd.read_csv('nasdaq100.csv', header=0, names=['value', 'label'])
symbols = list(nasdaq['value'])

close = StockCorr(symbols, 100).get_top_abs_correlations(15).get_df()


# Dash layout


app.layout = html.Div(className="container", children=[
                html.Div(className="row", children=[
                    html.Div(className="col-md-3", children=[
                        html.Nav(className="navbar navbar-expand-md navbar-light", children=[
                            html.Div(className="collapse navbar-collapse", children=[
                                html.Ul(className="navbar-nav flex-column", children=[
                                    dcc.Location(id='url', refresh=False),
                                    dcc.Link('Overview', className="btn btn-primary", href="/"),
                                    #html.Br(),
                                    dcc.Link('Stock Analysis', className="btn btn-primary", href="/stock-analysis"),
                                ]),
                            ])
                        ])
                    ]),
                    html.Div(className="col-md", children=
                        html.Div(id='page-content'),
                    )
                ]),
            ])

overview_layout = html.Div(id='overview', className='container', children=[
    html.Div(className='page-header', children=
        html.H1(children='Overview Page'),
    ),
    html.Div(className='Primary', children=[
        html.Div(className="card text-white bg-primary mb-3", children=[
            html.Div(className="card-header", children=
                html.H5("Top Correlations")
            ),
            html.Div(className="card-body", children=[
                dash_table.DataTable(
                    id='corr-table',
                    columns=[{"name": i, "id": i} for i in close.columns],
                    data=close.to_dict('records'),
                    style_cell_conditional=[
                        {
                            'if': {'column_id': c},
                            "textAlign": 'left'
                        } for c in ['Stock A', 'Stock B']
                    ],
                    style_header={
                        'backgroundColor': 'rgb(100,100,100)',
                        'fontWeight':'bold',
                        'color':'white'
                    },
                    style_cell={
                        'color':'black'
                    }
                )
            ])
        ]),
    ])
])

stock_analysis_layout = html.Div(id='single-stock',className='container', children=[
    html.Div(className='page-header', children=
        html.H1(children=title)
    ),
    html.Div(children='''
        
    '''),
    html.Div(
        [
            html.Div(
                [
                    html.P('Select your stock below.', className='card-header'),
                    html.Div(
                    dcc.Dropdown(
                        id = 'stock-input',
                        options=[{'label': x, 'value':y} for y, x in nasdaq.values],
                        value='TSLA',
                        className='text-secondary',
                        multi=False
                    ),
                    className='card-body'
                    ),
                    
                ],
                className='card text-white bg-primary mb-5',
                
            ),
        ], className='container'
    ),
    html.Div(className='jumobotron', children=
        dcc.Graph(
            id='stock-graph-line',
            #figure=fig
        )
    ),
])

@app.callback(
    Output(component_id='stock-graph-line', component_property='figure'),
    Input(component_id='stock-input', component_property='value'),
    suppress_callback_exceptions = True
)
def update_stock_symbol(input_value):
    df = StockData(input_value, 60).delta('close').get_df()
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"colspan":2}, None],
                                [{},{}]],
                        subplot_titles=("Price History","Daily Close Delta", "Daily Close Delta(%)")
    )

    '''

    To-Do -- Add Multi Symbol Traces

    for symbol in input_value:
        fig.append_trace({'x':df.index,'y':df[symbol].close, 'type':'scatter','name':'Price [Close]'},1,1)    
    
    '''

    fig.append_trace({'x':df.index,'y':df.close, 'type':'scatter','name':'Price [Close]'},1,1)
    fig.append_trace({'x':df.index,'y':df.open, 'type':'scatter','name':'Price [Open]'},1,1)
    fig.append_trace({'x':df.index,'y':df['close'].rolling(7).mean(), 'type':'scatter','name':'Rolling 7 Day Mean'},1,1)

    fig.append_trace({'x':df.index,'y':df.delta_close, 'type':'scatter','name':'Delta [Close]'},2,1)

    fig.append_trace({'x':df.index,'y':df.delta_close_pct, 'type':'scatter','name':'Delta [Close]'},2,2)


    fig['layout'].update(height=1000, title=input_value, template="plotly_dark")
    return fig


# Update the page contents
@app.callback(dash.dependencies.Output('page-content', 'children'),
                [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/stock-analysis':
        return stock_analysis_layout
    else:
        return overview_layout

if __name__ == '__main__':
    app.run_server(debug=True)
