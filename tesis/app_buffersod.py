import collections
import json
from collections import defaultdict
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback, Dash
import dash_core_components as dcc

from procesamiento_input_paper import get_viajes_xy_paradas_subidas_bajadas, read_consolidado_parada, \
    read_consolidado_parada_metro

viajes = get_viajes_xy_paradas_subidas_bajadas(1000)
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


def filter_viajes_by_origen(viajes: pd.DataFrame, ps):
    return viajes[viajes['paraderosubida'] == ps]


def filter_viajes_by_destino(viajes: pd.DataFrame, pb):
    return viajes[viajes['paraderobajada'] == pb]


def filter_viajes_by_origen_and_destino(viajes: pd.DataFrame, ps, pb):
    return viajes[(viajes['paraderosubida'] == ps) & (viajes['paraderobajada'] == pb)]


def get_selector_parada(dic_paradas, dic_parada_metro):
    paraderos = list(set(list(dic_paradas.keys()) + list(dic_parada_metro.keys())))
    return dcc.Dropdown([{'label': p, 'value': p} for p in paraderos], paraderos[0], id='selector_parada_buffers')


def get_selector_tipo_buffers():
    tipo = ['Origen', 'Destino']
    return dcc.Dropdown([{'label': p, 'value': p} for p in tipo], tipo[1], id='selector_tipo_buffers')


app = Dash(__name__)
app.layout = html.Div([
    html.H4("Análisis de buffers"),
    html.Hr(),
    dbc.Row([
        dbc.Col(["Paradero"], width=3),
        dbc.Col([get_selector_parada(dic_paradas, dic_paradas_metro)], width=3),
        dbc.Col(["Tipo"], width=3),
        dbc.Col([get_selector_tipo_buffers()], width=3),
    ]),
    dbc.Row([
        dbc.Col(["Numero de viajes"], width=3),
        dbc.Col(["Numero de origenes/destinos"], width=3),
    ])
])


@app.callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return f'You have selected {value}'
