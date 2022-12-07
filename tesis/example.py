import dash_html_components as html
import dash_leaflet as dl
from dash import Dash
from dash.dependencies import Output, Input
from dash_extensions.javascript import assign
import json

with open("georef-united-states-of-america-state.geojson") as f:
    gj = json.load(f)
print(gj)
features = gj['features'][0]
# Color the feature saved in the hideout prop in a particular way (grey).
style_handle = assign("""function(feature, context){
    const match = context.props.hideout &&  context.props.hideout.properties.name === feature.properties.name;
    if(match) return {weight:5, color:'#666', dashArray:''};
}""")
# Create example app.
app = Dash()
app.layout = html.Div([
    dl.Map(center=[39, -98], zoom=4, children=[
        dl.TileLayer(),
        dl.GeoJSON(gj, id="states",
                   options=dict(style=style_handle), hideout=dict(click_feature=None))
    ], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"),
])
# Update the feature saved on the hideout prop on click.
app.clientside_callback("function(feature){return feature}", Output("states", "hideout"),
                        [Input("states", "click_feature")])

if __name__ == '__main__':
    app.run_server()
