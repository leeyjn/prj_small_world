import sqlite3
import pandas as pd
import ast  # 문자열로 저장된 리스트 변환용

DB_PATH = "db/network_analysis.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # users 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            gender TEXT,
            grade REAL,
            school_id REAL,
            friends_num INTEGER
        )
    """)

    # friendships 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            user_id INTEGER,
            friend_id INTEGER,
            PRIMARY KEY (user_id, friend_id)
        )
    """)

    # events 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            user_id INTEGER,
            event_datetime TEXT,
            event_key TEXT,
            date TEXT
        )
    """)

    # friend_requests 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_requests (
            receive_user_id INTEGER,
            send_user_id INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

def load_csv_to_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 유저 정보 데이터 로드
    df_users = pd.read_csv("data/votes_user_total.csv")
    df_users["friend_id_list"] = df_users["friend_id_list"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else [])

    for _, row in df_users.iterrows():
        cursor.execute("INSERT INTO users (user_id, gender, grade, school_id, friends_num) VALUES (?, ?, ?, ?, ?)", 
                       (row["user_id"], row["gender"], row["grade"], row["school_id"], row["friends_num"]))

    for _, row in df_users.iterrows():
        user_id = row["user_id"]
        for friend_id in row["friend_id_list"]:
            cursor.execute("INSERT OR IGNORE INTO friendships (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    load_csv_to_db()
    print("데이터베이스 구축 완료")
