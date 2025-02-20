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

# ✅ 레이아웃 설정 (네트워크 시각화 + 친구 수 변화 그래프 + 이벤트 변화 그래프)
app.layout = html.Div([
    html.H1("📊 유저 네트워크 & 이벤트 변화 시각화", style={"color": "black", "text-align": "left", "margin-left": "20px"}),

    html.Div([
        # 🌐 네트워크 시각화
        html.Div([
            html.H3("🌐 네트워크 시각화", style={"color": "black", "text-align": "center"}),
            cyto.Cytoscape(
                id="cyto-graph",
                layout={"name": "cose", "gravity": 0.2},
                style={"height": "600px", "width": "100%", "border": "1px solid lightgray", "backgroundColor": "#F8F9FA"},
                elements=[],
                stylesheet=[
                    {"selector": "node", "style": {"content": "data(label)", "color": "#000000", "background-color": "#FFD700", "font-size": "14px"}},
                    {"selector": "edge", "style": {"width": 2, "line-color": "#1E90FF"}},
                ],
            )
        ], style={"width": "50%", "padding": "10px", "margin-left": "20px"}),

        # 📈 친구 수 변화 그래프
        html.Div([
            html.H3("📈 친구 수 변화", style={"color": "black", "text-align": "center"}),
            dcc.Graph(id="friend-count-graph", style={"height": "600px", "width": "100%", "backgroundColor": "#F8F9FA"})
        ], style={"width": "50%", "padding": "10px", "margin-right": "20px"}),
    ], style={"display": "flex", "flex-direction": "row", "width": "100%", "justify-content": "center", "align-items": "center"}),

    # 🔥 이벤트 발생 변화 그래프 추가
    html.Div([
        html.H3("🔥 이벤트 발생 변화", style={"color": "black", "text-align": "center"}),
        dcc.Graph(id="event-count-graph", style={"height": "500px", "width": "100%", "backgroundColor": "#F8F9FA"})
    ], style={"width": "90%", "margin": "auto", "padding": "10px", "border-radius": "10px", "border": "1px solid gray"}),
])

# ✅ 네트워크 데이터 저장 변수
latest_network_data = []
latest_user_id = None  # 현재 선택된 유저 저장

def get_network_data(user_id, selected_date):
    """선택된 유저의 네트워크 데이터를 가져옴"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?"
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

def get_event_summary(user_id):
    """유저의 이벤트 발생 데이터를 가져옴 (user_event_summary 기반)"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT event_date, event_key, SUM(event_count) as total_count
        FROM user_event_summary
        WHERE user_id = ?
        GROUP BY event_date, event_key
        ORDER BY event_date
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    return df

@server.route("/update_network", methods=["POST"])
def update_network():
    global latest_network_data, latest_user_id
    data = request.get_json()
    selected_user = data["selected_user"]
    selected_date = pd.to_datetime(data["selected_date"]).date()

    latest_user_id = selected_user  # 현재 선택된 유저 저장
    latest_network_data = get_network_data(selected_user, selected_date)

    # 🔥 디버깅: 데이터 정상 로드 확인
    if latest_network_data:
        print(f"✅ 네트워크 데이터 로드 완료 (노드 수: {len(latest_network_data)})")
    else:
        print("⚠️ 네트워크 데이터가 없음!")

    return jsonify(latest_network_data)

@app.callback(
    Output("cyto-graph", "elements"),
    [Input("cyto-graph", "id")]
)
def update_graph(_):
    return latest_network_data

@app.callback(
    Output("friend-count-graph", "figure"),
    [Input("cyto-graph", "id")]
)
def update_friend_count_graph(_):
    """친구 수 변화 그래프 업데이트"""
    if not latest_network_data or not latest_user_id:
        return px.line(title="No Data", labels={"date": "날짜", "friend_count": "친구 수"})

    df_friends = get_event_summary(latest_user_id)

    if df_friends.empty:
        return px.line(title="No Data", labels={"date": "날짜", "friend_count": "친구 수"})

    fig = px.line(df_friends, x="event_date", y="total_count", color="event_key", markers=True, 
                  title=f"🔥 {latest_user_id}의 이벤트 발생 변화")
    fig.update_layout(paper_bgcolor="#F8F9FA", plot_bgcolor="#F8F9FA", font=dict(color="black"))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
