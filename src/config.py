import os
from dotenv import load_dotenv
import urllib.parse

# ✅ .env 파일 로드
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# ✅ Supabase 설정 불러오기
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

# ✅ PostgreSQL 개별 변수로 변환 (URL 디코딩 적용)
url = urllib.parse.urlparse(SUPABASE_DB_URL)

SUPABASE_DB_CONFIG = {
    "dbname": url.path[1:],  # "/postgres" → "postgres"
    "user": urllib.parse.unquote(url.username),  # 사용자명 디코딩
    "password": urllib.parse.unquote(url.password),  # 비밀번호 URL 디코딩
    "host": url.hostname,
    "port": url.port,
}

# ✅ 디버깅 로그 추가
print("✅ Supabase 설정이 올바르게 로드되었습니다!")
print(f"🔗 Supabase URL: {SUPABASE_URL}")
print(f"🗄️  PostgreSQL Host: {SUPABASE_DB_CONFIG['host']}")
print(f"👤 DB User: {SUPABASE_DB_CONFIG['user']}")
print(f"🔑 DB Password: {SUPABASE_DB_CONFIG['password']} (길이: {len(SUPABASE_DB_CONFIG['password'])}글자)")
