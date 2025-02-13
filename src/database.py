import sqlite3
import pandas as pd
import os

# ✅ SQLite 데이터베이스 경로 설정
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("✅ SQLite 데이터베이스 연결 성공!")

# ✅ 1️⃣ `users` 테이블에 `created_at` 컬럼 추가 (없을 경우)
cursor.execute("PRAGMA table_info(users);")
columns = [col[1] for col in cursor.fetchall()]
if "created_at" not in columns:
    print("⚠️ 'created_at' 컬럼이 없습니다. 추가 중...")
    cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT;")
    print("✅ 'created_at' 컬럼 추가 완료!")

# ✅ 2️⃣ votes_user_total.csv에서 `created_at` 데이터 로드
print("📤 'votes_user_total.csv'에서 `created_at` 데이터 로드 중...")
df_users = pd.read_csv("C:/Users/pc/Python_Projects/final_project/final_data/hackle/votes_user_total.csv")

# ✅ NaN 값 처리
df_users["created_at"] = df_users["created_at"].fillna("")

# ✅ 3️⃣ `users` 테이블의 `created_at` 값 업데이트
print("📤 'users' 테이블의 `created_at` 데이터 업데이트 중...")
for _, row in df_users.iterrows():
    cursor.execute("""
        UPDATE users
        SET created_at = ?
        WHERE user_id = ?
    """, (row["created_at"], row["user_id"]))

# ✅ 변경 사항 저장 및 종료
conn.commit()
conn.close()
print("✅ 모든 데이터를 성공적으로 업데이트하였습니다!")
