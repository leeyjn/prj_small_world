import sqlite3
import pandas as pd

# ✅ SQLite 데이터베이스 연결
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)

# ✅ 1️⃣ 테이블 구조 확인 (`PRAGMA table_info`)
print("📌 [INFO] 'users' 테이블 구조 확인:")
df_table_info = pd.read_sql_query("PRAGMA table_info(users);", conn)
print(df_table_info)

# ✅ 2️⃣ `created_at` 컬럼이 있는지 확인
if "created_at" not in df_table_info["name"].values:
    print("⚠️ 'created_at' 컬럼이 없습니다. 추가 중...")
    conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT;")
    print("✅ 'created_at' 컬럼 추가 완료!")
else:
    print("✅ 'created_at' 컬럼이 이미 존재합니다.")

# ✅ 3️⃣ `users` 테이블의 `created_at` 값 확인
print("\n📌 [INFO] 'users' 테이블의 가입 날짜 (최대 10개 샘플):")
df_created_at = pd.read_sql_query("SELECT user_id, created_at FROM users ORDER BY created_at ASC LIMIT 10;", conn)
print(df_created_at)

# ✅ SQLite 연결 종료
conn.close()
print("✅ SQLite 연결 종료")
