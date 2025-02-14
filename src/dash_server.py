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

# ✅ Table Layout 적용 (2x2 그리드)
app.layout = html.Div([
    html.H1("📊 유저 네트워크 성장 과정 시각화", style={"color": "white", "text-align": "left", "margin-left": "20px"}),

    html.Div([
        # 🔹 유저 정보 (왼쪽 상단)
        html.Div([
            html.H3("👤 유저 정보", style={"color": "white"}),
            html.P("유저 ID: ", id="selected-user-text", style={"color": "white", "font-size": "16px"}),
            html.P("가입 날짜: ", id="user-join-date", style={"color": "white", "font-size": "16px"}),
        ], style={"width": "50%", "background-color": "#333", "padding": "20px", "border-radius": "10px"}),

        # 🔹 친구 수 변화 그래프 (오른쪽 상단)
        html.Div([
            html.H3("📈 친구 수 변화", style={"color": "white"}),
            dcc.Graph(id="friend-count-graph", style={"height": "350px", "width": "100%"})
        ], style={"width": "50%", "background-color": "#222", "padding": "20px", "border-radius": "10px"}),
    ], style={"display": "flex", "width": "100%", "gap": "20px"}),  # 상단 두 개 박스 정렬

    html.Div([
        # 🔹 네트워크 시각화 (왼쪽 하단)
        html.Div([
            html.H3("🌐 네트워크 시각화", style={"color": "white"}),
            cyto.Cytoscape(
                id="cyto-graph",
                layout={"name": "cose"},
                style={"height": "500px", "width": "100%", "border": "1px solid lightgray", "backgroundColor": "#1E1E1E"},
                elements=[],
                stylesheet=[
                    {"selector": "node", "style": {"content": "data(label)", "color": "white", "background-color": "#4A90E2", "font-size": "14px"}},
                    {"selector": "edge", "style": {"width": 2, "line-color": "white"}},
                ],
            )
        ], style={"width": "50%", "background-color": "#333", "padding": "20px", "border-radius": "10px"}),

        # 🔹 추가 정보 패널 (오른쪽 하단)
        html.Div([
            html.H3("📊 네트워크 지표", style={"color": "white"}),
            html.P("총 네트워크 노드 수: ", id="network-node-count", style={"color": "white", "font-size": "16px"}),
            html.P("총 네트워크 엣지 수: ", id="network-edge-count", style={"color": "white", "font-size": "16px"}),
        ], style={"width": "50%", "background-color": "#222", "padding": "20px", "border-radius": "10px"}),
    ], style={"display": "flex", "width": "100%", "gap": "20px"}),  # 하단 두 개 박스 정렬
], style={"display": "flex", "flex-direction": "column", "align-items": "center", "gap": "30px"})
