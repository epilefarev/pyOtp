import dash_bootstrap_components as dbc
from dash import html


def creador_tarjeta(enlace_imagen, titulo, parrafo, enlace_pagina):
    card = dbc.Card(
        [
            dbc.CardImg(src=enlace_imagen, top=True),
            dbc.CardBody(
                [
                    html.H4(titulo, className="card-title"),
                    html.P(
                        parrafo,
                        className="card-text",
                    ),
                    dbc.NavLink("Ver análisis", href=enlace_pagina)
                    # dbc.Button("Ver análisis", color="primary", id="boton_id"),
                ]
            ),
        ],
        style={"width": "18rem"},
    )
    return card


layout_inicio = dbc.Row([
    dbc.Col(creador_tarjeta("assets/favicon.ico", "Análisis de IDS", "Distribución de días observados por ID",
                            "http://127.0.0.1:8070/id"), width=3),
    dbc.Col(creador_tarjeta("assets/favicon.ico", "Análisis de OD", "Distribución de orígenes y destinos de viajes",
                            "http://127.0.0.1:8070/od"), width=3),
    dbc.Col(
        creador_tarjeta("assets/favicon.ico", "Análisis Buffers OD", "Análisis de alternativas de viajes por par OD",
                        "http://127.0.0.1:8070/buffersod"), width=3)
])
