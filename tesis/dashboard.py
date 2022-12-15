import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from diseño.home.home import SIDEBAR_STYLE, SIDEBAR_HIDEN, CONTENT_STYLE, CONTENT_STYLE1
from app_inicio import layout_inicio
from app_id_dias_observados import layout_id
from app_buffersod import layout_buffer
from app_od import layout_od


# iniciamos app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                suppress_callback_exceptions=True)
app.title = 'Smartrip'
server = app.server

# parte superior de la app
navbar = dbc.NavbarSimple(
    children=[
        dbc.Button(["HOME"], outline=True, color="primary", className="mr-1", id="btn_sidebar"),
    ],
    brand="Recomendador de viajes Smart",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
)

paginas = ['source', 'id', 'od', 'buffersod']
# barra de menu
sidebar = html.Div(
    [
        html.H6(["H", html.I(className="fa-solid fa-location-dot"), "M", "E"], className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Inicio", href="/source", id="source-link"),
                dbc.NavLink("Ids", href="/id", id="id-link"),
                dbc.NavLink("Origen-Destino", href="/od", id="od-link"),
                dbc.NavLink("Buffers OD", href="/buffersod", id="buffersod-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style=SIDEBAR_STYLE,
)

# contenido de la pagina
content = html.Div(
    id="page-content",
    style=CONTENT_STYLE
)

app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
    ],
)


@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],
    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"{i}-link", "active") for i in
     paginas],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False, False
    return [pathname == f"/{i}" for i in paginas]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    # ['source', 'reclutamiento', 'convocatoria', 'historial', 'estadistica', 'maquina']
    if pathname in ["/", "/source"]:
        return layout_inicio
    elif pathname == "/id":
        return layout_id
    elif pathname == "/od":
        return layout_od
    elif pathname == "/buffersod":
        return layout_buffer

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True, port=8070)
