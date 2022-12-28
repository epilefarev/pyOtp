import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from procesamiento_input_paper import read_input_small, contar_observaciones_id

df = read_input_small(chunksize=3000)
id_counts = contar_observaciones_id(df)

layout_id = html.Div([
    html.H4('Distribución de ids y días observados de la base de datos'),
    html.Hr(),
    dbc.Row([
        dbc.Col([dcc.Graph(id="graph_ids")], width=9),
        dbc.Col([
            dbc.Row([dcc.Graph(id="total_viajes_ids")]),
            dbc.Row([dcc.Graph(id="total_ids")])
        ], width=3),
    ]),
    html.Hr(),
    html.P("Filtro:"),
    dcc.Slider(id="filter", min=0, max=20, value=0,
               marks={0: '0', 5: '5', 10: '10', 15: '15', 20: '20'}),
])


@callback(
    Output("graph_ids", "figure"),
    Output("total_viajes_ids", "figure"),
    Output("total_ids", "figure"),
    Input("filter", "value"))
def display_color(filter):
    data = id_counts  # replace with your own data source
    data = [d for d in data if d >= filter]
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        value=200,
        delta={'reference': 160},
        gauge={
            'axis': {'visible': False}},
        domain={'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(
        value=120,
        gauge={
            'shape': "bullet",
            'axis': {'visible': False}},
        domain={'x': [0.05, 0.5], 'y': [0.15, 0.35]}))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=300,
        domain={'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
        mode="delta",
        value=40,
        domain={'row': 1, 'column': 1}))

    fig.update_layout(
        grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
        template={'data': {'indicator': [{
            'title': {'text': "Speed"},
            'mode': "number+delta+gauge",
            'delta': {'reference': 90}}]
        }})

    fig = px.histogram(data, range_x=[0, 20])
    fig.update_xaxes(title="N° de días observados")
    fig.update_yaxes(title="N° ids observados")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      # plot_bgcolor='rgba(0,0,0,0)',
                      showlegend=False, height=600)
    fig_viajes = go.Figure(go.Indicator(
        mode="number",
        value=sum(data), title="Total de viajes"))
    fig_viajes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                             # plot_bgcolor='rgba(0,0,0,0)',
                             showlegend=False, height=300)

    fig_ids = go.Figure(go.Indicator(
        mode="number",
        value=len(data), title="Total de ids"))
    fig_ids.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                          # plot_bgcolor='rgba(0,0,0,0)',
                          showlegend=False, height=300)

    return fig, fig_viajes, fig_ids
