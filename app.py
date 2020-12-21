from re import template
import dash
from dash_html_components.Nav import Nav
from dash_html_components.Ul import Ul
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_html_components.Div import Div
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import alpaca_trade_api as tradeapi
from config import *

class StockData:
    def __init__(self, symbol, timeframe) -> None:
        self.symbol = symbol
        api = tradeapi.REST(
                    key_id=key_id,
                    secret_key=secret_key,
                    base_url=base_url
        )
        df = api.get_barset(self.symbol, 'day', limit=timeframe).df
        self.df = df[self.symbol]
    
    def get_df(self):
        return self.df

    def delta(self, col):
        df_copy = self.df.copy()
        df_copy['delta_'+col] = self.df[col] - self.df[col].shift(1)
        df_copy.loc[df_copy.index[0], 'delta_'+col]=0
        df_copy['delta_'+col+'_pct'] = round((self.df[col] - self.df[col].shift(1))/self.df[col].shift(1)*100,2)
        df_copy.loc[df_copy.index[0], 'delta_'+col+'_pct']=0
        self.df = df_copy
        return self

class StockCorr:
    def __init__(self, symbols, timeframe) -> None:
        self.symbols = symbols
        api = tradeapi.REST(
                    key_id=key_id,
                    secret_key=secret_key,
                    base_url=base_url
        )
        df = api.get_barset(symbols, 'day', limit=timeframe).df

        self.close = pd.DataFrame()
        for symbol in self.symbols:
            self.close[symbol] = df[(symbol,'close')]

    def get_top_abs_correlations(self, n=5):
        def get_redundant_pairs(df):
            pairs_to_drop = set()
            cols = df.columns
            for i in range(0, df.shape[1]):
                for j in range(0, i+1):
                    pairs_to_drop.add((cols[i], cols[j]))
            return pairs_to_drop

        au_corr = self.close.corr().abs().unstack()
        labels_to_drop = get_redundant_pairs(self.close)
        au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
        self.df = au_corr[0:n].to_frame()
        self.df = self.df.reset_index()
        self.df.columns = ['Stock A', 'Stock B', 'Corr']
        return self

    def get_df(self):
        return self.df
  

# Define Dash App Configurations
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], )
app.config.suppress_callback_exceptions = True
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
                        multi=True
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
