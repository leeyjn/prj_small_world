import sqlite3
import pandas as pd

# ✅ SQLite 데이터베이스 연결
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ 1️⃣ 데이터베이스에 있는 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📌 데이터베이스 테이블 목록:")
for table in tables:
    print("-", table[0])

# ✅ 2️⃣ 특정 테이블 데이터 조회 (`users` 테이블 예시)
table_name = "users"  # 원하는 테이블 이름 입력
df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5;", conn)

print(f"\n📌 {table_name} 테이블 데이터 샘플:")
print(df)

# ✅ 연결 종료
conn.close()
