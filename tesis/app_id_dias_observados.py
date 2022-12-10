import plotly.express as px
from dash import dcc, html, Input, Output, callback

from procesamiento_input_paper import read_input_small, contar_observaciones_id

df = read_input_small(chunksize=-1)
id_counts = contar_observaciones_id(df)

layout_id = html.Div([
    html.H4('Distribution'),
    dcc.Graph(id="graph"),
    html.P("Filtro:"),
    dcc.Slider(id="filter", min=0, max=20, value=0,
               marks={0: '0', 5: '5', 10: '10', 15: '15', 20: '20'}),
    html.Div(id="total_datos")
])


@callback(
    Output("graph", "figure"),
    Output("total_datos", "children"),
    Input("filter", "value"))
def display_color(filter):
    data = id_counts  # replace with your own data source
    data = [d for d in data if d >= filter]
    fig = px.histogram(data, range_x=[0, 20])
    return fig, html.P('Total datos {}'.format(len(data)))
