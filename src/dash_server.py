from flask import Flask, request, jsonify
import dash
from dash import dcc, html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import json
import pandas as pd
from data_loader import load_friend_requests
from network_builder import build_network

server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")

# 🔥 **Flask POST 요청 핸들러 추가**
@server.route("/update_network", methods=["POST"])
def update_graph():
    """ Streamlit에서 받은 데이터를 Dash에서 네트워크로 변환 """
    data = request.get_json()
    
    if not data or "selected_user" not in data or "selected_date" not in data:
        print("⚠️ 올바른 데이터가 전달되지 않음:", data)
        return jsonify([])

    selected_user = data["selected_user"]
    selected_date = data["selected_date"]

    print(f"🟢 요청된 유저: {selected_user}, 날짜: {selected_date}")

    df_requests = load_friend_requests(selected_user)

    if df_requests.empty:
        print(f"⚠️ 유저 {selected_user}의 친구 요청 데이터 없음")
        return jsonify([])

    # 선택한 날짜 이전의 친구 요청만 필터링
    df_requests["created_at"] = pd.to_datetime(df_requests["created_at"])
    df_filtered = df_requests[df_requests["created_at"] <= pd.to_datetime(selected_date)]

    if df_filtered.empty:
        print(f"⚠️ {selected_date}까지의 친구 요청이 없음")
        return jsonify([])

    print(f"🔄 {selected_date}까지 {len(df_filtered)}개의 친구 요청 포함")

    G = build_network(selected_user, df_filtered)

    cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
    cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

    print(f"✅ 생성된 네트워크 - 노드: {len(cyto_nodes)}, 엣지: {len(cyto_edges)}")

    return jsonify(cyto_nodes + cyto_edges)

# Dash Layout
app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        elements=[],
    )
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
