import streamlit as st

def user_selector(df_users):
    """유저 선택 드롭다운"""
    return st.selectbox("유저를 선택하세요:", df_users["user_id"].astype(str))

def date_slider(min_date, max_date):
    """유저의 네트워크 성장 슬라이딩 바"""
    return st.slider("네트워크 빌드 시간 선택", min_value=min_date, max_value=max_date, value=min_date)
