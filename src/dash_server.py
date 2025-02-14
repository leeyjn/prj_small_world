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

    return network_nodes + edges

# ✅ API 엔드포인트: Streamlit이 요청을 보낼 때 실행됨
@server.route("/update_network", methods=["POST"])
def update_network():
    data = request.json
    user_id = data.get("selected_user")
    selected_date = pd.to_datetime(data.get("selected_date")).date()

    if not user_id or not selected_date:
        return jsonify({"error": "유효하지 않은 요청"}), 400

    network_data = get_network_data(user_id, selected_date)
    print(f"📊 업데이트된 네트워크 데이터 (노드 {len(network_data)}개): {network_data}")

    return jsonify(network_data)

# ✅ Cytoscape 그래프 업데이트 로직
@app.callback(
    Output("cyto-graph", "elements"),
    Input("cyto-graph", "id")  # 더미 Input (자동 업데이트를 위해)
)
def update_graph(_):
    """네트워크 그래프 업데이트"""
    try:
        with server.test_request_context():
            # ✅ Streamlit에서 마지막으로 요청한 데이터 사용
            latest_request = request.get_json()
            if not latest_request:
                return []

            user_id = latest_request.get("selected_user")
            selected_date = pd.to_datetime(latest_request.get("selected_date")).date()
            network_data = get_network_data(user_id, selected_date)
            return network_data
    except Exception as e:
        print(f"🚨 그래프 업데이트 중 오류 발생: {e}")
        return []

# ✅ Dash 서버 실행
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
