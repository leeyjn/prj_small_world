import json
import networkx as nx
import pandas as pd
from flask import Flask, request, jsonify
import dash
from dash import dcc, html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

# ✅ Flask 서버 생성
server = Flask(__name__)

# ✅ Dash 앱 생성 및 Flask와 연결
app = dash.Dash(__name__, server=server, url_base_pathname="/dash/")

# ✅ 네트워크 그래프 초기 레이아웃
app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    cyto.Cytoscape(
        id="cyto-graph",
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        elements=[],  # 🔥 초기에는 빈 리스트
    ),
])

# ✅ 친구 요청 데이터 로드 함수
def load_friend_requests(user_id):
    """SQLite에서 해당 유저의 친구 요청 데이터 로드"""
    import sqlite3

    DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT user_id, requests_list FROM friend_requests_optimized
        WHERE user_id = ?
    """

    df_requests = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df_requests.empty:
        return pd.DataFrame(columns=["send_user_id", "created_at"])

    # JSON 데이터 변환
    df_requests["requests_list"] = df_requests["requests_list"].apply(json.loads)
    requests_expanded = []
    
    for _, row in df_requests.iterrows():
        for req in row["requests_list"]:
            requests_expanded.append({
                "send_user_id": req["send_user_id"],
                "created_at": req["created_at"]
            })
    
    return pd.DataFrame(requests_expanded)

# ✅ 네트워크 그래프 생성 함수
def build_network(selected_user, df_filtered):
    """네트워크 그래프를 생성"""
    G = nx.Graph()
    G.add_node(selected_user)

    for _, row in df_filtered.iterrows():
        send_user = str(row["send_user_id"])  # 🔥 ID를 문자열로 변환 (Cytoscape 호환성 문제 해결)
        G.add_node(send_user)
        G.add_edge(str(selected_user), send_user)

    return G

# ✅ Streamlit → Dash 요청 처리
@server.route("/update_network", methods=["POST"])
def update_graph():
    """ Streamlit에서 받은 데이터를 Dash에서 네트워크로 변환 """
    data = request.get_json()

    if not data or "selected_user" not in data or "selected_date" not in data:
        print("⚠️ 올바른 데이터가 전달되지 않음:", data)
        return jsonify([])

    selected_user = str(data["selected_user"])  # 🔥 ID를 문자열로 변환
    selected_date = data["selected_date"]

    print(f"🟢 요청된 유저: {selected_user}, 날짜: {selected_date}")

    df_requests = load_friend_requests(selected_user)

    if df_requests.empty:
        print(f"⚠️ 유저 {selected_user}의 친구 요청 데이터 없음")
        return jsonify([])

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
    print(f"📊 네트워크 데이터: {cyto_nodes + cyto_edges}")  # 🔥 디버깅 코드

    return jsonify(cyto_nodes + cyto_edges)

# ✅ 네트워크 그래프를 동적으로 업데이트
@app.callback(
    Output("cyto-graph", "elements"),
    Input("cyto-graph", "id")  # 🔥 업데이트 트리거
)
def update_elements(_):
    """ Dash 네트워크 그래프 동적 업데이트 """
    print(f"🔄 네트워크 그래프 업데이트 요청됨")

    try:
        with open("latest_request.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    selected_user = str(data.get("selected_user", None))  # 🔥 ID를 문자열로 변환
    selected_date = data.get("selected_date", None)

    if not selected_user or not selected_date:
        return []

    df_requests = load_friend_requests(selected_user)
    df_requests["created_at"] = pd.to_datetime(df_requests["created_at"])
    df_filtered = df_requests[df_requests["created_at"] <= pd.to_datetime(selected_date)]

    G = build_network(selected_user, df_filtered)

    cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
    cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

    print(f"✅ 네트워크 업데이트 완료 - 노드: {len(cyto_nodes)}, 엣지: {len(cyto_edges)}")

    return cyto_nodes + cyto_edges

# ✅ Dash 서버 실행
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
