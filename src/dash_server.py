import dash
import dash_cytoscape as cyto
from dash import dcc, html
import sqlite3
import pandas as pd
import json
from dash.dependencies import Input, Output, State
from flask import Flask, request, jsonify
import plotly.express as px

# ✅ SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ Flask 기반 Dash 서버 생성
server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname="/dash/")

# ✅ 네트워크 데이터 저장 변수
latest_network_data = []

def get_network_data(user_id, selected_date):
    """선택된 유저의 네트워크 데이터를 가져옴"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        print("⚠️ 유저의 친구 요청 데이터 없음")
        return []

    df["requests_list"] = df["requests_list"].apply(json.loads)
    network_nodes = [{"data": {"id": str(user_id), "label": str(user_id)}}]  # 시작 노드

    edges = []
    for _, row in df.iterrows():
        for req in row["requests_list"]:
            req_date = pd.to_datetime(req["created_at"]).date()
            if req_date <= selected_date:
                friend_id = str(req["send_user_id"])
                network_nodes.append({"data": {"id": friend_id, "label": friend_id}})
                edges.append({"data": {"source": str(user_id), "target": friend_id}})

    print(f"✅ 네트워크 노드: {len(network_nodes)}, 엣지: {len(edges)}")
    return network_nodes + edges

# ✅ HORIZONTAL FLEX LAYOUT 적용
app.layout = html.Div([
    html.H1("📊 유저 네트워크 성장 과정 시각화", style={"color": "white", "text-align": "left", "margin-left": "20px"}),

    html.Div([
        html.Div([
            html.H3("🌐 네트워크 시각화", style={"color": "white"}),
            cyto.Cytoscape(
                id="cyto-graph",
                layout={"name": "cose"},
                style={"height": "700px", "width": "100%", "backgroundColor": "#1E1E1E"},
                elements=[]
            )
        ], style={"width": "50%", "padding": "10px"}),

        html.Div([
            html.H3("📈 친구 수 변화", style={"color": "white"}),
            dcc.Graph(id="friend-count-graph", style={"height": "700px", "width": "100%"})
        ], style={"width": "50%", "padding": "10px"}),
    ], style={"display": "flex", "flex-direction": "row", "width": "100%", "justify-content": "center"})
])


@server.route("/update_network", methods=["POST"])
def update_network():
    global latest_network_data
    data = request.get_json()
    
    if not data or "selected_user" not in data or "selected_date" not in data:
        return jsonify({"error": "Missing parameters"}), 400

    selected_user = data["selected_user"]
    selected_date = pd.to_datetime(data["selected_date"]).date()

    print(f"🔄 네트워크 업데이트 요청 - 유저: {selected_user}, 날짜: {selected_date}")

    latest_network_data = get_network_data(selected_user, selected_date)

    return jsonify(latest_network_data)


@app.callback(
    Output("cyto-graph", "elements"),
    [Input("cyto-graph", "id")]
)
def update_graph(_):
    return latest_network_data if latest_network_data else []


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
