import os
from collections import defaultdict

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from typing import List

enlace_input_tesis = "G:\Mi unidad\descarga_chrome\paper_tesis"


def read_input() -> pd.DataFrame:
    print("Leyendo input")
    df = pd.read_csv(os.path.join(enlace_input_tesis, "datos_jacque.csv"))
    print(list(df.columns))
    print(df.describe())
    print("Filtramos ids None")
    df = df[df['id'] != "-"]
    print(df.describe())
    return df


def contar_observaciones_id(df):
    print("Contando ids")
    id_counts = df['id'].value_counts().tolist()
    return id_counts


df = read_input()
id_counts = contar_observaciones_id(df)

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Distribution'),
    dcc.Graph(id="graph"),
    html.P("Filtro:"),
    dcc.Slider(id="filter", min=0, max=20, value=0,
               marks={0: '0', 5: '5', 10: '10', 15: '15', 20: '20'}),
    html.Div(id="total_datos")
])


@app.callback(
    Output("graph", "figure"),
    Output("total_datos", "children"),
    Input("filter", "value"))
def display_color(filter):
    data = id_counts  # replace with your own data source
    data = [d for d in data if d >= filter]
    fig = px.histogram(data, range_x=[0, 20])
    return fig, html.P('Total datos {}'.format(len(data)))


app.run_server(debug=True)
