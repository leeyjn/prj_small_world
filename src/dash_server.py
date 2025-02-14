import dash
import dash_cytoscape as cyto
import dash_html_components as html
import sqlite3
import pandas as pd
import json
from dash.dependencies import Input, Output
from flask import Flask, request, jsonify

# ✅ SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ Flask 기반 Dash 서버 생성
server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname="/dash/")

# ✅ 네트워크 그래프 초기 상태
app.layout = html.Div([
    html.H2("📊 유저 네트워크 성장 과정"),
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"height": "600px", "width": "100%", "border": "1px solid lightgray"},
        elements=[]  # 초기엔 빈 그래프
    )
])

# ✅ 전역 변수로 네트워크 데이터 저장
latest_network_data = []


def get_network_data(user_id, selected_date):
    """선택된 유저의 네트워크 데이터를 가져옴"""
    conn = sqlite3.connect(DB_PATH)

    # ✅ 해당 유저의 친구 요청 내역 가져오기
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


@server.route("/update_network", methods=["POST"])
def update_network():
    global latest_network_data
    data = request.json
    user_id = data.get("selected_user")
    selected_date = pd.to_datetime(data.get("selected_date")).date()

    if not user_id or not selected_date:
        return jsonify({"error": "유효하지 않은 요청"}), 400

    network_data = get_network_data(user_id, selected_date)
    latest_network_data = network_data  # 전역 변수 업데이트
    print(f"📊 업데이트된 네트워크 데이터 (노드 {len(network_data)}개): {network_data}")

    return jsonify(network_data)


@app.callback(
    Output("cyto-graph", "elements"),
    Input("cyto-graph", "id")
)
def update_graph(_):
    """네트워크 그래프 업데이트"""
    try:
        if latest_network_data:
            print(f"🟢 Cytoscape 업데이트: {len(latest_network_data)} 요소")
            return latest_network_data
        else:
            print("⚠️ Cytoscape 업데이트 실패: 네트워크 데이터 없음")
            return []
    except Exception as e:
        print(f"🚨 그래프 업데이트 중 오류 발생: {e}")
        return []


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
