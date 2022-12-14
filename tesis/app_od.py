from collections import defaultdict

import dash_leaflet as dl
from dash import html

from procesamiento_input_paper import get_viajes_xy_paradas_subidas_bajadas


def get_point_map_od(lp, lx, ly):
    dict_position_weight = defaultdict(None)
    for i in range(len(lp)):
        ps = lp[i]
        if ps in dict_position_weight:
            x, y, w = dict_position_weight[ps]
            dict_position_weight[ps] = x, y, w + 1
        else:
            dict_position_weight[ps] = lx[i], ly[i], 1
    w_max = 0
    for ps in dict_position_weight:
        x, y, w = dict_position_weight[ps]
        if w >= w_max:
            w_max = w
    tupla = [(dict_position_weight[ps], ps) for ps in dict_position_weight]
    tupla = [(x, y, w, w / w_max * 10, ps) for (x, y, w), ps in tupla]
    return tupla


def get_cluster(tupla, name):
    markers = []
    for x, y, v, w, p in tupla:
        markers.append(
            dl.CircleMarker(
                center=(y, x),
                radius=5,
                color="green",
                weight=w,
                # icon=icon,
                children=[dl.Tooltip(p),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(
                                      v))
                          ])],
            )
        )
    cluster = dl.MarkerClusterGroup(id=name, children=markers)
    return cluster


def get_markers(tupla, color, name):
    markers = []
    for x, y, v, w, p in tupla:
        markers.append(
            dl.CircleMarker(
                center=(y, x),
                radius=5,
                color=color,
                weight=w,
                # icon=icon,
                children=[dl.Tooltip(p),
                          dl.Popup([
                              html.P(
                                  "Observaciones: {}".format(
                                      v))
                          ])],
            )
        )
    return dl.FeatureGroup(markers, id=name)





viajes = get_viajes_xy_paradas_subidas_bajadas()

lps = list(viajes['paraderosubida'])
lpb = list(viajes['paraderobajada'])
lxs = list(viajes['xs'])
lys = list(viajes['ys'])
lxb = list(viajes['xb'])
lyb = list(viajes['yb'])

tupla_ps = get_point_map_od(lps, lxs, lys)
tupla_pb = get_point_map_od(lpb, lxb, lyb)

subidas_cluster = dl.FeatureGroup([get_cluster(tupla_ps, "Subidas Cluster")])
bajadas_cluster = dl.FeatureGroup([get_cluster(tupla_pb, "Bajadas Cluster")])
subidas_markers = get_markers(tupla_ps, "green", "Subidas")
bajadas_markers = get_markers(tupla_pb, "red", "Bajadas")

my_map = dl.Map(center=[lys[0], lxs[0]], zoom=10, children=[
    dl.LayersControl(
        [
            dl.BaseLayer(
                dl.TileLayer(),
                name="Base",
                checked=True,
            ),
            dl.Overlay(
                [subidas_cluster],
                name="Subidas Cluster",
                checked=False,
            ),
            dl.Overlay(
                [bajadas_cluster],
                name="Bajadas Cluster",
                checked=False,
            ),
            dl.Overlay(
                [subidas_markers],
                name="Subidas",
                checked=True,
            ),
            dl.Overlay(
                [bajadas_markers],
                name="Bajadas",
                checked=True,
            ),
        ],
    ),
],
                style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}, id="map")

layout_od = html.Div([
    html.H4("Distribución espacial de origenes y destinos de viajes"),
    html.Hr(),
    my_map
])
