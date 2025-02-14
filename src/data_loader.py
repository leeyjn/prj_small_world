import sqlite3
import pandas as pd
import json

DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

def load_users():
    """유저 목록 로드 (가입일 순 정렬)"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT user_id, friends_num, created_at FROM users ORDER BY created_at ASC"
    df_users = pd.read_sql_query(query, conn)
    conn.close()
    return df_users

def load_friend_requests(user_id):
    """특정 유저의 친구 요청 기록 로드"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?"
    df_requests = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df_requests.empty:
        return pd.DataFrame(columns=["receive_user_id", "send_user_id", "created_at", "status"])

    requests_list = json.loads(df_requests.iloc[0]["requests_list"])
    df_requests_expanded = pd.DataFrame(requests_list)
    df_requests_expanded["created_at"] = pd.to_datetime(df_requests_expanded["created_at"], errors="coerce")
    return df_requests_expanded
