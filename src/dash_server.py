from flask import Flask
import dash
from dash import dcc, html
import dash_cytoscape as cyto
import sqlite3
import pandas as pd
import networkx as nx
import json

# ✅ Flask 앱 생성
server = Flask(__name__)
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")

# ✅ SQLite 데이터 로드
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)

# ✅ 1️⃣ 네트워크 그래프 데이터 로드
query_users = """
    SELECT user_id, friends_num, created_at
    FROM users
    ORDER BY created_at ASC
"""
df_users = pd.read_sql_query(query_users, conn)

# ✅ 예제 유저 선택 (처음 가입한 유저)
selected_user = df_users.iloc[0]["user_id"]

# ✅ 친구 요청 데이터 가져오기
query_friend_requests = """
    SELECT user_id, requests_list
    FROM friend_requests_optimized
    WHERE user_id = ?
"""
df_requests = pd.read_sql_query(query_friend_requests, conn, params=(selected_user,))

# ✅ JSON 데이터를 DataFrame으로 변환
friend_requests = []
for _, row in df_requests.iterrows():
    user_id = row["user_id"]
    requests_list = json.loads(row["requests_list"]) if isinstance(row["requests_list"], str) else []
    
    for request in requests_list:
        friend_requests.append({
            "receive_user_id": user_id,
            "send_user_id": request["send_user_id"],
            "created_at": request["created_at"],
            "status": request["status"]
        })

df_requests_expanded = pd.DataFrame(friend_requests)

# ✅ 2️⃣ 네트워크 그래프 데이터 구성
G = nx.Graph()
G.add_node(int(selected_user), label=str(selected_user))  # 초기 노드

for _, row in df_requests_expanded.iterrows():
    G.add_node(row["send_user_id"], label=str(row["send_user_id"]))
    G.add_edge(int(selected_user), row["send_user_id"])

# ✅ Cytoscape 노드 & 엣지 변환
cyto_nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes]
cyto_edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges]

# ✅ Dash 레이아웃 설정
app.layout = html.Div([
    html.H3("📡 네트워크 성장 과정"),
    cyto.Cytoscape(
        id="cyto-graph",
        elements=cyto_nodes + cyto_edges,
        layout={"name": "cose"},
        style={"width": "100%", "height": "600px", "border": "1px solid black"},
        stylesheet=[
            {"selector": "node", "style": {"content": "data(label)", "text-valign": "center", "background-color": "#0084ff"}},
            {"selector": "edge", "style": {"line-color": "#9dbaea", "width": 2}},
        ]
    )
])

# ✅ Dash 서버 실행
if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
