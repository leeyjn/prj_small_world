import sqlite3
import json
import pandas as pd

DB_PATH = "C:/Users/pc/Python_Projects/prj_small_world/db/network_analysis.db"

def load_users():
    """ users 테이블에서 유저 정보 가져오기 """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT user_id, gender, grade, school_id, friends_num, group_id, created_at FROM users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_friend_requests(user_id):
    """ 선택된 유저의 친구 요청 데이터를 JSON 변환 후 반환 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT requests_list FROM friend_requests_optimized WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0]:  # 값이 존재하면 JSON 변환
        requests_list = json.loads(result[0])
        return pd.DataFrame(requests_list)
    else:
        return pd.DataFrame(columns=["send_user_id", "status", "created_at"])

def load_friendships(user_id):
    """ 선택된 유저의 친구 리스트를 JSON 변환 후 반환 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT friend_list FROM friendships_optimized WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0]:
        friend_list = json.loads(result[0])  # JSON을 리스트로 변환
        return pd.DataFrame({"friend_id": friend_list})  # pandas DataFrame 변환
    else:
        return pd.DataFrame(columns=["friend_id"])  # 빈 데이터 반환
