from flask import Flask
import dash
from dash import dcc, html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
from data_loader import load_users, load_friend_requests
from network_builder import build_network

# ✅ Flask + Dash 앱 생성
server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")

# ✅ Dash 레이아웃 설정
app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    dcc.Store(id="selected-user", storage_type="memory"),  # ✅ 유저 선택 저장소
    dcc.Slider(id="time-slider", min=0, max=10, step=1, value=0),
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        elements=[],
        stylesheet=[
            {"selector": "node", "style": {"content": "data(label)", "background-color": "#0084ff"}},
            {"selector": "edge", "style": {"line-color": "#9dbaea", "width": 2}},
            {"selector": ".user-node", "style": {"background-color": "#ff5733", "label": "data(label)"}},
            {"selector": ".friend-edge", "style": {"line-color": "#00aaff", "width": 2}},
        ]
    )
])

# ✅ 네트워크 데이터 업데이트
@app.callback(
    Output("cyto-graph", "elements"),
    Input("selected-user", "data"),
    Input("time-slider", "value")
)
def update_graph(selected_user, time_index):
    print(f"🔍 선택된 유저: {selected_user}")  # ✅ 유저 선택 확인

    if not selected_user:
        print("⚠️ 유저가 선택되지 않음")
        return []

    df_requests = load_friend_requests(selected_user)

    if df_requests.empty:
        print("⚠️ 해당 유저의 친구 요청 데이터가 없음")
        return []

    selected_date = df_requests["created_at"].min() + pd.to_timedelta(time_index, unit="D")
    print(f"📅 선택된 날짜: {selected_date}")  # ✅ 날짜 확인

    G = build_network(selected_user, df_requests, selected_date)

    cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
    cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

    print(f"🛠️ 노드 개수: {len(cyto_nodes)}, 엣지 개수: {len(cyto_edges)}")  # ✅ 네트워크 크기 확인

    return cyto_nodes + cyto_edges

# ✅ Dash 서버 실행
if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
