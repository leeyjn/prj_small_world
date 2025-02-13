import sqlite3
import pandas as pd
import json
import os
import numpy as np

# ✅ 로컬 SQLite 데이터베이스 파일 경로 설정
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

# ✅ SQLite 연결
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("✅ SQLite 데이터베이스 연결 성공!")

# ✅ 기존 users 테이블 삭제
cursor.execute("DROP TABLE IF EXISTS users")

# ✅ 새로운 users 테이블 생성 (group_id 포함)
cursor.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        gender TEXT,
        grade INTEGER,
        school_id INTEGER,
        friends_num INTEGER,
        group_id INTEGER
    )
""")

# ✅ 2️⃣ Friendships 테이블 (JSON 형식으로 저장)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS friendships_optimized (
        user_id INTEGER PRIMARY KEY,
        friend_list TEXT  -- JSON 형태로 친구 ID 저장
    )
""")

# ✅ 3️⃣ Events 테이블 (JSON 형식으로 저장)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS events_optimized (
        user_id INTEGER PRIMARY KEY,
        events_list TEXT  -- JSON 형태로 이벤트 목록 저장
    )
""")

# ✅ 4️⃣ Friend Requests 테이블 (JSON 형식으로 저장)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS friend_requests_optimized (
        user_id INTEGER PRIMARY KEY,
        requests_list TEXT  -- JSON 형태로 친구 요청 목록 저장
    )
""")

# ✅ Users 데이터 삽입
print("📤 Users 데이터 업로드 중...")
df_users = pd.read_csv("C:/Users/pc/Python_Projects/final_project/final_data/hackle/votes_user_total.csv")

df_users = df_users.where(pd.notna(df_users), None)  # NaN을 None(SQL NULL)으로 변환
  # NaN 값을 None으로 변환
df_users["group_id"] = df_users["group_id"].apply(lambda x: None if pd.isna(x) else int(x))
df_users["school_id"] = df_users["school_id"].apply(lambda x: None if pd.isna(x) else int(x))
df_users["friends_num"] = df_users["friends_num"].apply(lambda x: None if pd.isna(x) else int(x))

for _, row in df_users.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, gender, grade, school_id, friends_num, group_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (row["user_id"], row["gender"], row["grade"], row["school_id"], row["friends_num"], row["group_id"]))

# ✅ Friendships 데이터 JSON 변환 후 삽입
print("📤 Friendships 데이터 JSON 변환 중...")
friendships_dict = {}
for _, row in df_users.iterrows():
    user_id = row["user_id"]
    friend_ids = json.loads(row["friend_id_list"]) if isinstance(row["friend_id_list"], str) else row["friend_id_list"]
    
    friendships_dict[user_id] = friend_ids

print("📤 Friendships 데이터 SQLite 저장 중...")
for user_id, friend_list in friendships_dict.items():
    cursor.execute("""
        INSERT OR REPLACE INTO friendships_optimized (user_id, friend_list)
        VALUES (?, ?)
    """, (user_id, json.dumps(friend_list)))

# ✅ Events 데이터 JSON 변환 후 삽입
print("📤 Events 데이터 JSON 변환 중...")
df_events = pd.read_csv("C:/Users/pc/Python_Projects/final_project/final_data/2023_24hackle/df_hackle_processed_20230718-08.csv")

events_dict = {}
for _, row in df_events.iterrows():
    user_id = row["user_id"]
    event_info = {
        "event_datetime": row["event_datetime"],
        "event_key": row["event_key"],
        "date": row["date"]
    }
    
    if user_id not in events_dict:
        events_dict[user_id] = []
    events_dict[user_id].append(event_info)

print("📤 Events 데이터 SQLite 저장 중...")
for user_id, events_list in events_dict.items():
    cursor.execute("""
        INSERT OR REPLACE INTO events_optimized (user_id, events_list)
        VALUES (?, ?)
    """, (user_id, json.dumps(events_list)))

# ✅ Friend Requests 데이터 JSON 변환 후 삽입
print("📤 Friend Requests 데이터 JSON 변환 중...")
df_requests = pd.read_csv("C:/Users/pc/Python_Projects/final_project/final_data/pjdata/votes/accounts_friendrequest.csv")

requests_dict = {}
for _, row in df_requests.iterrows():
    receive_user = row["receive_user_id"]
    request_info = {
        "send_user_id": row["send_user_id"],
        "status": row["status"],
        "created_at": row["created_at"]
    }
    
    if receive_user not in requests_dict:
        requests_dict[receive_user] = []
    requests_dict[receive_user].append(request_info)

print("📤 Friend Requests 데이터 SQLite 저장 중...")
for user_id, requests_list in requests_dict.items():
    cursor.execute("""
        INSERT OR REPLACE INTO friend_requests_optimized (user_id, requests_list)
        VALUES (?, ?)
    """, (user_id, json.dumps(requests_list)))

# ✅ 변경 사항 저장 및 연결 종료
conn.commit()
conn.close()
print("🎉 ✅ 모든 데이터를 JSON 최적화하여 SQLite 데이터베이스에 성공적으로 저장하였습니다!")
