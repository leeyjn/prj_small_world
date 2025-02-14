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
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        elements=[],
    )
])

@app.callback(
    Output("cyto-graph", "elements"),
    Input("cyto-graph", "id")
)
def update_graph(_):
    selected_user = request.args.get("selected_user", None)

    if not selected_user:
        print("⚠️ 유저 선택 안됨")
        return []

    df_requests = load_friend_requests(selected_user)

    if df_requests.empty:
        print(f"⚠️ 유저 {selected_user}의 친구 요청 데이터 없음")
        return []

    G = build_network(selected_user, df_requests)

    cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
    cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

    print(f"🟢 노드 개수: {len(cyto_nodes)}, 엣지 개수: {len(cyto_edges)}")

    return cyto_nodes + cyto_edges

if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
