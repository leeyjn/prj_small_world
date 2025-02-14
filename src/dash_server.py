from flask import Flask, request, jsonify
import dash
from dash import dcc, html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
from data_loader import load_friend_requests
from network_builder import build_network

server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")

app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    dcc.Store(id="selected-user", storage_type="memory"),  
    dcc.Slider(id="time-slider", min=0, max=10, step=1, value=0),
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        elements=[],
    )
])

@app.callback(
    Output("cyto-graph", "elements"),
    Input("selected-user", "data"),
    Input("time-slider", "value")
)
def update_graph(selected_user, time_index):
    if not selected_user:
        return []

    df_requests = load_friend_requests(selected_user)
    
    if df_requests.empty:
        return []

    selected_date = df_requests["created_at"].min() + pd.to_timedelta(time_index, unit="D")
    G = build_network(selected_user, df_requests, selected_date)

    cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
    cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

    return cyto_nodes + cyto_edges

if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
