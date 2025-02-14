import streamlit as st
import requests
import pandas as pd
from data_loader import load_users, load_friend_requests
from ui_components import user_selector, date_slider

df_users = load_users()
selected_user = user_selector(df_users)

df_requests = load_friend_requests(selected_user)

if not df_requests.empty:
    df_requests["created_at"] = pd.to_datetime(df_requests["created_at"], errors="coerce")
    min_date = df_requests["created_at"].min().date()
    max_date = df_requests["created_at"].max().date()

    selected_date = date_slider(min_date, max_date)

    st.write(f"**✅ 선택된 유저:** {selected_user}")
    st.write(f"**📅 선택된 날짜:** {selected_date}")

    try:
        response = requests.post("http://localhost:8050/update_network", json={
            "selected_user": selected_user, 
            "selected_date": str(selected_date)
        })
        print(f"📤 Dash 서버로 요청 보냄: {selected_user}, {selected_date}")
        print(f"🔄 Dash 서버 응답 코드: {response.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("🚨 Dash 서버 실행을 확인하세요!")

st.write("### 네트워크 성장 과정")
st.components.v1.iframe("http://localhost:8050/dash/", height=700)
