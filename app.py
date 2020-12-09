from re import template
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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


# Define Dash App Configurations
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
title = 'Stock Analysis'

# Define Subplot
'''
fig = make_subplots(
    rows = 2, cols = 2,
    specs=[[{'type':'xy'}, {'type':'xy'}],
    [{'type':'xy'},{'type':'xy'}]]
)'''


# Dash layout
app.layout = html.Div(children=[
    html.H1(children=title),
    html.Div(children='''
        Dash based stock graphing tool.
    '''),
    html.Div(
        [
            html.Div(
                [
                    html.P('Choose Stock:'),
                    dcc.Dropdown(
                        id = 'stock-input',
                        options=[
                            {'label': 'Tesla', 'value': 'TSLA'},
                            {'label': 'IBM', 'value': 'IBM'},
                            {'label': 'Apple', 'value': 'AAPL'},
                        ],
                        value='TSLA'
                        #labelStyle={'display': 'inline-block'}
                    ),
                ],
                className='six columns',
                style={'margin-top': '10'}
            ),
        ], className='row'
    ),

    dcc.Graph(
        id='stock-graph-line',
        #figure=fig
    )
])

@app.callback(
    Output(component_id='stock-graph-line', component_property='figure'),
    Input(component_id='stock-input', component_property='value')
)
def update_stock_symbol(input_value):
    df = StockData(input_value, 60).delta('close').get_df()
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"colspan":2}, None],
                                [{},{}]],
                        subplot_titles=("Price History","Daily Close Delta", "Daily Close Delta(%)")
    )

    fig.append_trace({'x':df.index,'y':df.close, 'type':'scatter','name':'Price [Close]'},1,1)
    fig.append_trace({'x':df.index,'y':df.open, 'type':'scatter','name':'Price [Open]'},1,1)
    fig.append_trace({'x':df.index,'y':df['close'].rolling(7).mean(), 'type':'scatter','name':'Rolling 7 Day Mean'},1,1)

    fig.append_trace({'x':df.index,'y':df.delta_close, 'type':'scatter','name':'Delta [Close]'},2,1)

    fig.append_trace({'x':df.index,'y':df.delta_close_pct, 'type':'scatter','name':'Delta [Close]'},2,2)


    fig['layout'].update(height=1000, width=2000, title=input_value, template="plotly_dark")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)