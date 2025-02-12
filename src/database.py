import requests
from config import SUPABASE_URL, SUPABASE_KEY

# ✅ Supabase API 연결 테스트
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)

if response.status_code == 200:
    print("✅ Supabase 연결 성공!")
else:
    print(f"❌ Supabase 연결 실패! 상태 코드: {response.status_code}")
