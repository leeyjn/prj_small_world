import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ✅ SQLite 데이터베이스 경로
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ Streamlit UI 설정
st.title("📈 이벤트 빈도 변화 분석")

# ✅ 데이터베이스 연결 및 유저 목록 가져오기
conn = sqlite3.connect(DB_PATH)
df_users = pd.read_sql_query("SELECT user_id FROM users ORDER BY user_id ASC", conn)
conn.close()

# ✅ 유저 선택 (드롭다운 리스트)
selected_user = st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str).tolist())

def get_event_data(user_id):
    """ 특정 유저의 event_logs 데이터에서 event_key 별 발생 빈도 계산 """
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT date(event_datetime) AS event_date, event_key, COUNT(*) AS event_count
        FROM event_logs
        WHERE user_id = ?
        GROUP BY event_date, event_key
        ORDER BY event_date;
    """
    df_events = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df_events

df_events = get_event_data(selected_user)

if not df_events.empty:
    df_pivot = df_events.pivot(index="event_date", columns="event_key", values="event_count").fillna(0)

    fig = px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, markers=True,
                  title=f"📊 {selected_user}의 이벤트 발생 빈도 변화",
                  labels={"value": "이벤트 발생 횟수", "event_date": "날짜"})

    fig.update_layout(paper_bgcolor="#2C2C54", plot_bgcolor="#2C2C54", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ 해당 유저의 이벤트 데이터가 없습니다.")
