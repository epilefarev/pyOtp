import collections
import json
import logging
from collections import defaultdict

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
import plotly.graph_objects as go
from dash import html, Input, Output, callback, State, dcc

from procesamiento_input_paper import get_viajes_xy_paradas_subidas_bajadas, read_consolidado_parada, \
    read_consolidado_parada_metro

logger_buffer = logging.getLogger()

viajes = get_viajes_xy_paradas_subidas_bajadas(-1)
# leemos consolidado de paradas
paradas, dic_paradas = read_consolidado_parada()
# leemos consolidado de parada de metro
paradas_metro, dic_paradas_metro = read_consolidado_parada_metro()


def get_buffer(paradero_central):
    color = 'green'
    try:
        lon, lat = dic_paradas[paradero_central]
    except:
        lon, lat = dic_paradas_metro[paradero_central]
    markers = [dl.Circle(center=(lat, lon), radius=500, color=color, fillOpacity=0.1, dashArray='10,20')]
    return dl.FeatureGroup(markers)


def get_buffer_destino(paradero_central):
    color = 'red'
    try:
        lon, lat = dic_paradas[paradero_central]
    except:
        lon, lat = dic_paradas_metro[paradero_central]
    markers = [dl.Circle(center=(lat, lon), radius=500, color=color, fillOpacity=0.1, dashArray='10,20')]
    return dl.FeatureGroup(markers)


def get_paraderos_origen(paraderos_buffers, viajes_buffers):
    markers = []
    for p in paraderos_buffers:

        n_viajes = len(viajes_buffers[viajes_buffers['paraderosubida'] == p])
        color = 'green' if n_viajes != 0 else 'grey'

        try:
            lon, lat = dic_paradas[p]

        except:
            try:
                lon, lat = dic_paradas_metro[p]
            except:
                continue
        markers.append(
            dl.CircleMarker(
                center=(lat, lon),
                radius=5,
                color=color,
                # icon=icon,
                children=[dl.Tooltip(p),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(n_viajes))
                          ])],
            )
        )
    return dl.FeatureGroup(markers)


def get_paraderos_destino(paraderos_buffers, viajes_buffers):
    markers = []
    for p in paraderos_buffers:

        n_viajes = len(viajes_buffers[viajes_buffers['paraderobajada'] == p])
        color = 'red' if n_viajes != 0 else 'grey'

        try:
            lon, lat = dic_paradas[p]

        except:
            try:
                lon, lat = dic_paradas_metro[p]
            except:
                continue
        markers.append(
            dl.CircleMarker(
                center=(lat, lon),
                radius=5,
                color=color,
                # icon=icon,
                children=[dl.Tooltip(p),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(n_viajes))
                          ])],
            )
        )
    return dl.FeatureGroup(markers)


def get_mapa_buffer(viajes_buffers, paraderos_buffer, parada, paraderos_buffers_destino, paradero_destino):
    marcadores_paraderos_buffer = get_paraderos_origen(paraderos_buffer, viajes_buffers)
    marcadores_paraderos_buffer_destino = get_paraderos_destino(paraderos_buffers_destino, viajes_buffers)
    buffers_map = get_buffer(parada)
    buffers_map_destino = get_buffer_destino(paradero_destino)
    try:
        lon, lat = dic_paradas[parada]
    except:
        lon, lat = dic_paradas_metro[parada]
    my_map = dl.Map(center=(lat, lon), zoom=15, children=[
        dl.LayersControl(
            [
                dl.BaseLayer(
                    dl.TileLayer(),
                    name="Base",
                    checked=True,
                ),
                dl.Overlay(
                    [buffers_map],
                    name="Buffer Origen",
                    checked=True,
                ),
                dl.Overlay(
                    [buffers_map_destino],
                    name="Buffer Destino",
                    checked=True,
                ),
                dl.Overlay(
                    [marcadores_paraderos_buffer],
                    name="Paraderos en Origen",
                    checked=True,
                ),
                dl.Overlay(
                    [marcadores_paraderos_buffer_destino],
                    name="Paraderos en Destino",
                    checked=True,
                )
            ],
        ),
    ],
                    style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}, id="map_buffer")
    return my_map


def distancia_puntos_latlon(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return (((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5) * 111100


def __get_bufferes_paraderos(dic_paradas: collections.defaultdict,
                             dic_parada_metro: collections.defaultdict) -> collections.defaultdict:
    """
    preconsulta de buffers que hay que actualizar cuando se actualiza el consolidado de paraderos
    :param dic_paradas:
    :param dic_parada_metro:
    :return:
    """
    paraderos = list(set(list(dic_paradas.keys()) + list(dic_parada_metro.keys())))
    output = defaultdict(list)
    no_output = defaultdict(list)
    n = 1
    for p1 in paraderos:
        print(n)
        n += 1

        try:
            lon1, lat1 = dic_paradas[p1]
        except Exception:
            try:
                lon1, lat1 = dic_parada_metro[p1]
            except Exception:
                continue
        for p2 in paraderos:
            if p1 == p2:
                no_output[p1].append(p2)
                continue
            elif p2 in output[p1]:
                continue
            elif p2 in no_output[p1]:
                continue
            else:
                try:
                    lon2, lat2 = dic_paradas[p2]
                except Exception:
                    try:
                        lon2, lat2 = dic_parada_metro[p2]
                    except Exception:
                        continue
                d = distancia_puntos_latlon(lat1, lon1, lat2, lon2)
                if d <= 500:
                    output[p1].append(p2)
                    output[p2].append(p1)
                else:
                    no_output[p1].append(p2)
                    no_output[p2].append(p1)

    a_file = open("salida/buffers.json", "w")
    json.dump(output, a_file, indent=4)
    a_file.close()

    return output


def read_json_buffers():
    """
    dic[paradero]=list[paradero]
    :return:
    """
    with open("salida/buffers.json", "r", encoding='utf-8') as file:
        data = json.load(file)
    return data


buffers = read_json_buffers()


def filter_viajes_by_origen(viajes: pd.DataFrame, ps):
    return viajes[viajes['paraderosubida'] == ps]


def filter_viajes_by_destino(viajes: pd.DataFrame, pb):
    return viajes[viajes['paraderobajada'] == pb]


def filter_viajes_by_origen_and_destino(viajes: pd.DataFrame, ps, pb):
    return viajes[(viajes['paraderosubida'] == ps) & (viajes['paraderobajada'] == pb)]


def filter_viajes_by_origenes_and_destinos(viajes: pd.DataFrame, ps, pb):
    return viajes[(viajes['paraderosubida'].isin(ps)) & (viajes['paraderobajada'].isin(pb))]


def get_selector_parada(dic_paradas, dic_parada_metro):
    paraderos = list(set(list(dic_paradas.keys()) + list(dic_parada_metro.keys())))
    return dcc.Dropdown([{'label': p, 'value': p} for p in paraderos], 'LAS REJAS', id='selector_parada_origen')


def opciones_paradero_destino(parada_origen: str, viajes: pd.DataFrame):
    paraderos = list(viajes[viajes['paraderosubida'] == parada_origen]['paraderobajada'].unique())

    return [{'label': "{}: {} viajes".format(p, len(filter_viajes_by_origenes_and_destinos(viajes,
                                                                                           buffers[parada_origen] + [
                                                                                               parada_origen],
                                                                                           buffers[p] + [p]))),
             'value': p} for p in paraderos]


def figura_ranking(df: pd.DataFrame, x, y, ascending=True):
    df = df.sort_values(by=[x], ascending=ascending)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(df[x]),
        y=list(df[y]),
        orientation='h',
        marker=dict(
            color='deeppink',
            line=dict(color='rgb(248, 248, 249)', width=1)
        )
    ))

    fig.update_layout(
        # height=150,
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            zeroline=True,
            # domain=[0, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            zeroline=True,
            dtick=1,
            type='category'
        ),
        barmode='stack',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    return fig


layout_viajes_od = html.Div([
    html.H4("Análisis de buffers"),
    html.Hr(),
    dbc.Row([
        dbc.Col(["Paradero Origen"], width=3),
        dbc.Col([get_selector_parada(dic_paradas, dic_paradas_metro)], width=3),
        dbc.Col(["Paradero Destino"], width=3),
        dbc.Col([dcc.Dropdown(id='selector_parada_destino')], width=3),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(html.Div(id='map_viajes_od'), width=9),
        dbc.Col([dbc.Row(dcc.Graph(id="numero_viajes_od")),
                 dbc.Row(dcc.Graph(id="numero_origenes_od")),
                 dbc.Row(dcc.Graph(id="numero_destinos_od")), dbc.Row(dcc.Graph(id="numero_tarjetas_od")), ], width=3)
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.H4("Ranking de estrategias par OD"),
            dbc.Row(dcc.Graph(id="estrategias_viajes_od")),
            html.Hr(),
            html.H4("Ranking Alternativas par OD"),
            dbc.Row(dcc.Graph(id="alternativas_viajes_od"))])
    ]),

])


def distinguir_alternativas_viajes(viajes: pd.DataFrame):
    estrategias_od = viajes['estrategia_viaje'].value_counts()
    values = estrategias_od.keys().tolist()
    counts = estrategias_od.tolist()
    estrategias_od = pd.DataFrame()
    estrategias_od['Estrategia'] = values
    estrategias_od['Observaciones'] = counts

    fig_rank_estrategia = figura_ranking(estrategias_od, 'Observaciones', "Estrategia", True)

    alternativas_od = viajes['alternativa_viaje'].value_counts()
    values = alternativas_od.keys().tolist()
    counts = alternativas_od.tolist()
    alternativas_od = pd.DataFrame()
    alternativas_od['Alternativa'] = values
    alternativas_od['Observaciones'] = counts

    fig_rank_alternativa = figura_ranking(alternativas_od, 'Observaciones', "Alternativa", True)

    return fig_rank_estrategia, fig_rank_alternativa


@callback(
    Output('selector_parada_destino', 'options'),
    [Input("selector_parada_origen", "value")]
)
def update_options_destinos(origen):
    return opciones_paradero_destino(origen, viajes)


@callback(
    Output('selector_parada_destino', 'value'),
    [Input('selector_parada_destino', 'options')]
)
def update_value_destinos(opciones):
    try:
        return opciones[0]['value']
    except:
        return None


@callback(
    Output('map_viajes_od', 'children'),
    Output('numero_viajes_od', 'figure'),
    Output('numero_origenes_od', 'figure'),
    Output('numero_destinos_od', 'figure'),
    Output('numero_tarjetas_od', 'figure'),
    Output('estrategias_viajes_od', 'figure'),
    Output('alternativas_viajes_od', 'figure'),
    [Input('selector_parada_destino', 'value')], State('selector_parada_origen', 'value')
)
def update_output(parada_destino, parada_origen):
    paraderos_buffers = buffers[parada_origen] + [parada_origen]
    paraderos_buffers_destino = buffers[parada_destino] + [parada_destino]
    logger_buffer.info("paradero dentro del buffer")
    logger_buffer.info(paraderos_buffers)
    # filtramos viajes dentro del biffer de origen y destino
    viajes_od = viajes[
        (viajes['paraderosubida'].isin(paraderos_buffers)) & (viajes['paraderobajada'].isin(paraderos_buffers_destino))]

    fig_rank_estrategia, fig_rank_alternativa = distinguir_alternativas_viajes(viajes_od)

    my_map = get_mapa_buffer(viajes_od, paraderos_buffers, parada_origen, paraderos_buffers_destino,
                             parada_destino)

    fig_viajes = go.Figure(go.Indicator(
        mode="number",
        value=len(viajes_od), title="Total de viajes"))
    fig_viajes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                             # plot_bgcolor='rgba(0,0,0,0)',
                             showlegend=False, height=300)

    fig_destinos = go.Figure(go.Indicator(
        mode="number",
        value=len(
            list(viajes_od['paraderobajada'].unique())), title="Total de destinos"))
    fig_destinos.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                               # plot_bgcolor='rgba(0,0,0,0)',
                               showlegend=False, height=300)

    fig_origenes = go.Figure(go.Indicator(
        mode="number",
        value=len(
            list(viajes_od['paraderosubida'].unique())), title="Total de orígenes"))
    fig_origenes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                               # plot_bgcolor='rgba(0,0,0,0)',
                               showlegend=False, height=300)

    fig_tarjetas = go.Figure(go.Indicator(
        mode="number",
        value=len(
            list(viajes_od['id'].unique())), title="Total de tarjetas"))
    fig_tarjetas.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                               # plot_bgcolor='rgba(0,0,0,0)',
                               showlegend=False, height=300)

    return my_map, fig_viajes, fig_destinos, fig_origenes, fig_tarjetas, fig_rank_estrategia, fig_rank_alternativa
