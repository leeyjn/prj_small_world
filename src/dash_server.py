import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
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

# ✅ HORIZONTAL FLEX LAYOUT 적용
app.layout = html.Div([
    # 🔹 상단 제목
    html.Div([
        html.H1("📊 유저 네트워크 성장 과정 시각화", style={"color": "white", "text-align": "left", "margin-left": "20px"})
    ], style={"width": "100%", "display": "flex", "justify-content": "flex-start"}),

    # 🔹 네트워크 시각화 + 친구 수 변화 그래프 **완전한 가로 정렬**
    html.Div([
        # 🔹 네트워크 시각화
        html.Div([
            html.H3("🌐 네트워크 시각화", style={"color": "white", "text-align": "center"}),
            cyto.Cytoscape(
                id="cyto-graph",
                layout={"name": "cose"},
                style={"height": "700px", "width": "100%", "border": "1px solid lightgray", "backgroundColor": "#1E1E1E"},
                elements=[],
                stylesheet=[
                    {"selector": "node", "style": {"content": "data(label)", "color": "white", "background-color": "#4A90E2", "font-size": "14px"}},
                    {"selector": "edge", "style": {"width": 2, "line-color": "white"}},
                ],
            )
        ], style={"width": "50%", "display": "flex", "flex-direction": "column", "justify-content": "center", "padding": "10px", "margin-left": "20px"}),

        # 🔹 친구 수 변화 그래프
        html.Div([
            html.H3("📈 친구 수 변화", style={"color": "white", "text-align": "center"}),
            dcc.Graph(id="friend-count-graph", style={"height": "700px", "width": "100%"})
        ], style={"width": "50%", "display": "flex", "flex-direction": "column", "justify-content": "center", "padding": "10px", "margin-right": "20px"}),
    ], style={"display": "flex", "flex-direction": "row", "width": "100%", "justify-content": "center", "align-items": "center"}),
])

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


def get_friend_count_data(user_id):
    """선택된 유저의 친구 수 변화를 시각화하기 위한 데이터 생성"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        return pd.DataFrame(columns=["date", "friend_count"])

    df["requests_list"] = df["requests_list"].apply(json.loads)

    friend_counts = {}
    for _, row in df.iterrows():
        for req in row["requests_list"]:
            req_date = pd.to_datetime(req["created_at"]).date()
            friend_counts[req_date] = friend_counts.get(req_date, 0) + 1

    # ✅ 날짜별 누적 친구 수 계산
    sorted_dates = sorted(friend_counts.keys())
    cumulative_friends = []
    total_friends = 0

    for date in sorted_dates:
        total_friends += friend_counts[date]
        cumulative_friends.append({"date": date, "friend_count": total_friends})

    return pd.DataFrame(cumulative_friends)


@server.route("/update_network", methods=["POST"])
def update_network():
    global latest_network_data
    data = request.get_json()
    selected_user = data["selected_user"]
    selected_date = pd.to_datetime(data["selected_date"]).date()

    latest_network_data = get_network_data(selected_user, selected_date)
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
    if not latest_network_data:
        return px.line(title="No Data", labels={"date": "날짜", "friend_count": "친구 수"})

    user_id = latest_network_data[0]["data"]["id"]
    df_friends = get_friend_count_data(user_id)

    if df_friends.empty:
        return px.line(title="No Data", labels={"date": "날짜", "friend_count": "친구 수"})

    fig = px.line(df_friends, x="date", y="friend_count", markers=True, title=f"📊 {user_id}의 친구 수 변화")
    fig.update_layout(paper_bgcolor="#1E1E1E", plot_bgcolor="#1E1E1E", font=dict(color="white"))
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
