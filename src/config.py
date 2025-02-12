import os
from dotenv import load_dotenv

# ✅ .env 파일 로드
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# ✅ Supabase 설정 불러오기
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("✅ Supabase 설정이 올바르게 로드되었습니다!")
print(f"🔗 Supabase URL: {SUPABASE_URL}")
