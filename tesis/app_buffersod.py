import collections
import json
from collections import defaultdict
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback, Dash, State, dcc
import dash_leaflet as dl
from procesamiento_input_paper import get_viajes_xy_paradas_subidas_bajadas, read_consolidado_parada, \
    read_consolidado_parada_metro
import logging
import plotly.graph_objects as go

logger_buffer = logging.getLogger()

viajes = get_viajes_xy_paradas_subidas_bajadas(3000)
# leemos consolidado de paradas
paradas, dic_paradas = read_consolidado_parada()
# leemos consolidado de parada de metro
paradas_metro, dic_paradas_metro = read_consolidado_parada_metro()


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


def get_selector_parada(dic_paradas, dic_parada_metro):
    paraderos = list(set(list(dic_paradas.keys()) + list(dic_parada_metro.keys())))
    return dcc.Dropdown([{'label': p, 'value': p} for p in paraderos], 'LOS LEONES', id='selector_parada_buffers')


def get_selector_tipo_buffers():
    tipo = ['Origen', 'Destino']
    return dcc.Dropdown([{'label': p, 'value': p} for p in tipo], tipo[1], id='selector_tipo_buffers')


layout_buffer = html.Div([
    html.H4("An??lisis de buffers"),
    html.Hr(),
    dbc.Row([
        dbc.Col(["Paradero"], width=3),
        dbc.Col([get_selector_parada(dic_paradas, dic_paradas_metro)], width=3),
        dbc.Col(["Tipo"], width=3),
        dbc.Col([get_selector_tipo_buffers()], width=3),
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([], width=10),
        dbc.Col([dbc.Button("Procesar", color="primary", className="me-1", id='procesarbuffer', n_clicks=0)], width=2),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='map_buffers_od'), width=9),
        dbc.Col([dbc.Row(dcc.Graph(id="numero_viajes_buffer")), dbc.Row(dcc.Graph(id="numero_od_buffer_2")),
                 dbc.Row(dcc.Graph(id="numero_od_buffer")), ], width=3)
]),

])

def get_buffer(tipo, paradero_central):
    if tipo == "Origen":
        color = 'green'
    else:
        color = 'red'
    try:
        lon, lat = dic_paradas[paradero_central]
    except:
        lon, lat = dic_paradas_metro[paradero_central]
    markers = [dl.Circle(center=(lat, lon), radius=500, color=color, fillOpacity=0.1, dashArray='10,20')]
    return dl.FeatureGroup(markers)


def get_paraderos_buffers(paraderos_buffers, tipo, viajes_buffers, paradero_central):
    markers = []
    for paradero in paraderos_buffers:
        if tipo == "Origen":
            n_viajes = len(viajes_buffers[viajes_buffers['paraderosubida'] == paradero])
            color = 'green' if n_viajes != 0 else 'grey'
        else:
            n_viajes = len(viajes_buffers[viajes_buffers['paraderobajada'] == paradero])
            color = 'red' if n_viajes != 0 else 'grey'
        try:
            lon, lat = dic_paradas[paradero]

        except:
            try:
                lon, lat = dic_paradas_metro[paradero]
            except:
                continue
        markers.append(
            dl.CircleMarker(
                center=(lat, lon),
                radius=5,
                color=color,
                # icon=icon,
                children=[dl.Tooltip(paradero),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(n_viajes))
                          ])],
            )
        )
    return dl.FeatureGroup(markers)


def get_paraderos_no_buffers(tipo, viajes_buffers):
    if tipo == "Origen":
        paraderos = viajes_buffers['paraderobajada'].unique()
        color = 'red'
    else:
        paraderos = viajes_buffers['paraderosubida']
        color = 'green'
    markers = []
    for paradero in paraderos:
        if tipo == "Origen":
            n_viajes = len(viajes_buffers[viajes_buffers['paraderobajada'] == paradero])
        else:
            n_viajes = len(viajes_buffers[viajes_buffers['paraderosubida'] == paradero])
        try:
            lon, lat = dic_paradas[paradero]

        except:
            try:
                lon, lat = dic_paradas_metro[paradero]
            except:
                continue
        markers.append(
            dl.CircleMarker(
                center=(lat, lon),
                radius=5,
                color=color,
                # icon=icon,
                children=[dl.Tooltip(paradero),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(n_viajes))
                          ])],
            )
        )
    return dl.FeatureGroup(markers)


def get_mapa_buffer(viajes_buffers, paraderos_buffer, parada, tipo):
    marcadores_paraderos_buffer = get_paraderos_buffers(paraderos_buffer, tipo, viajes_buffers, parada)
    buffers_map = get_buffer(tipo, parada)
    marcadores_paraderos_no_buffer = get_paraderos_no_buffers(tipo, viajes_buffers)
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
                    name="Buffer",
                    checked=True,
                ),
                dl.Overlay(
                    [marcadores_paraderos_buffer],
                    name="Paraderos en Buffer",
                    checked=True,
                ),
                dl.Overlay(
                    [marcadores_paraderos_no_buffer],
                    name="Paraderos no en Buffer",
                    checked=True,
                )
            ],
        ),
    ],
                    style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}, id="map_buffer")
    return my_map


@callback(
    Output('map_buffers_od', 'children'),
    Output('numero_viajes_buffer', 'figure'),
    Output('numero_od_buffer', 'figure'),
    Output('numero_od_buffer_2', 'figure'),
    [Input("procesarbuffer", "n_clicks")], State('selector_parada_buffers', 'value'),
    State('selector_tipo_buffers', 'value')
)
def update_output(n, parada, tipo):
    paraderos_buffers = buffers[parada] + [parada]
    logger_buffer.info("paradero dentro del buffer")
    logger_buffer.info(paraderos_buffers)
    if tipo == "Origen":
        viajes_parada = viajes[viajes['paraderosubida'].isin(paraderos_buffers)]
        my_map = get_mapa_buffer(viajes_parada, paraderos_buffers, parada, tipo)

        fig_viajes = go.Figure(go.Indicator(
            mode="number",
            value=len(viajes_parada), title="Total de viajes"))
        fig_viajes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                 # plot_bgcolor='rgba(0,0,0,0)',
                                 showlegend=False, height=300)

        fig_destinos = go.Figure(go.Indicator(
            mode="number",
            value=len(
                list(viajes_parada['paraderobajada'].unique())), title="Total de destinos"))
        fig_destinos.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                   # plot_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False, height=300)

        fig_origenes = go.Figure(go.Indicator(
            mode="number",
            value=len(
                list(viajes_parada['paraderosubida'].unique())), title="Total de or??genes"))
        fig_origenes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                   # plot_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False, height=300)

        return my_map, fig_viajes, fig_destinos, fig_origenes
    else:
        viajes_parada = viajes[viajes['paraderobajada'].isin(paraderos_buffers)]
        my_map = get_mapa_buffer(viajes_parada, paraderos_buffers, parada, tipo)
        fig_viajes = go.Figure(go.Indicator(
            mode="number",
            value=len(viajes_parada), title="Total de viajes"))
        fig_viajes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                 # plot_bgcolor='rgba(0,0,0,0)',
                                 showlegend=False, height=300)

        fig_destinos = go.Figure(go.Indicator(
            mode="number",
            value=len(
                list(viajes_parada['paraderobajada'].unique())), title="Total de destinos"))
        fig_destinos.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                   # plot_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False, height=300)

        fig_origenes = go.Figure(go.Indicator(
            mode="number",
            value=len(
                list(viajes_parada['paraderosubida'].unique())), title="Total de or??genes"))
        fig_origenes.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                   # plot_bgcolor='rgba(0,0,0,0)',
                                   showlegend=False, height=300)

        return my_map, fig_viajes, fig_destinos, fig_origenes
