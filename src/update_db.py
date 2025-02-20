import sqlite3
import pandas as pd

# ✅ 경로 설정 (CSV 파일과 SQLite DB)
DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"
CSV_PATH = "C:/Users/pc/Python_Projects/final_project/final_data/2023_24hackle/df_hackle_processed_20230718-08.csv"

# ✅ CSV 데이터 불러오기 (dtype 경고 해결)
df_hackle = pd.read_csv(CSV_PATH, dtype=str, low_memory=False)

# ✅ 'event_datetime'을 날짜 형식으로 변환
df_hackle["event_datetime"] = pd.to_datetime(df_hackle["event_datetime"])

# ✅ SQLite 데이터베이스 연결
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ `event_logs` 테이블 삭제 후 새로 생성
sql_create_event_logs = """
DROP TABLE IF EXISTS event_logs;

CREATE TABLE event_logs (
    user_id TEXT,
    session_id TEXT,
    event_datetime TIMESTAMP,
    event_key TEXT,
    item_name TEXT,
    page_name TEXT,
    class TEXT,
    gender TEXT,
    grade TEXT,
    school_id TEXT,
    friend_count INTEGER,
    votes_count INTEGER,
    heart_balance INTEGER,
    question_id TEXT,
    osname TEXT,
    osversion TEXT,
    versionname TEXT,
    device_id TEXT,
    date DATE
);
"""
cursor.executescript(sql_create_event_logs)
conn.commit()

# ✅ `event_logs` 테이블에 데이터 삽입
df_hackle.to_sql("event_logs", conn, if_exists="replace", index=False)

# ✅ `users` 테이블 업데이트 (최초 event_datetime을 created_at으로 설정)
df_users = df_hackle.groupby("user_id")["event_datetime"].min().reset_index()
df_users.rename(columns={"event_datetime": "created_at"}, inplace=True)
df_users.to_sql("users", conn, if_exists="replace", index=False)

# ✅ `user_event_summary` 테이블 삭제 후 새로 생성
sql_create_user_event_summary = """
DROP TABLE IF EXISTS user_event_summary;

CREATE TABLE user_event_summary (
    user_id TEXT,
    event_date DATE,
    hour INTEGER,
    event_key TEXT,
    event_count INTEGER,
    PRIMARY KEY (user_id, event_date, hour, event_key)
);
"""
cursor.executescript(sql_create_user_event_summary)
conn.commit()

# ✅ `user_event_summary` 업데이트 (핵심 이벤트 필터링)
sql_insert = """
INSERT INTO user_event_summary (user_id, event_date, hour, event_key, event_count)
SELECT 
    e.user_id,
    DATE(e.event_datetime) AS event_date,
    strftime('%H', e.event_datetime) AS hour,
    e.event_key,
    COUNT(*) AS event_count
FROM event_logs e
JOIN users u ON e.user_id = u.user_id
WHERE event_key IN ('complete_question', 'click_question_open')  -- 핵심 이벤트 필터링
AND DATE(u.created_at) >= '2023-07-18'  -- 2023_24hackle 데이터 반영
GROUP BY e.user_id, event_date, hour, e.event_key;
"""

cursor.executescript(sql_insert)
conn.commit()

# ✅ 완료 메시지 출력
print("✅ `event_logs`, `users`, `user_event_summary` 테이블 업데이트 완료!")

# ✅ 업데이트된 데이터 확인
df_check = pd.read_sql_query("SELECT * FROM user_event_summary LIMIT 10", conn)
print(df_check)

# ✅ 연결 종료
conn.close()
