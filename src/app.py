import sqlite3
import pandas as pd
import streamlit as st

# ✅ SQLite 데이터베이스 연결
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)

st.title("SQLite 데이터 조회")

# ✅ 테이블 선택
tables = ["users", "friendships_optimized", "events_optimized", "friend_requests_optimized"]
table_name = st.selectbox("조회할 테이블을 선택하세요:", tables)

# ✅ 선택한 테이블 데이터 조회
query = f"SELECT * FROM {table_name} LIMIT 10;"
df = pd.read_sql_query(query, conn)
st.write(df)

# ✅ 연결 종료
conn.close()
