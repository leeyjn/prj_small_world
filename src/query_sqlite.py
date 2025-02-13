import sqlite3
import pandas as pd

# ✅ SQLite 데이터베이스 연결
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)

# ✅ friend_requests_optimized 테이블 구조 확인
df_table_info = pd.read_sql_query("PRAGMA table_info(friend_requests_optimized);", conn)
print(df_table_info)

# ✅ 테이블 데이터 샘플 확인
df_sample = pd.read_sql_query("SELECT * FROM friend_requests_optimized LIMIT 5;", conn)
print(df_sample)

# ✅ 연결 종료
conn.close()
