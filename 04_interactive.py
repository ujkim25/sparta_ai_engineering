import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def initialize_session_state():
    if "counter" not in st.session_state:
        st.session_state.counter=0

    if "user_data" not in st.session_state:
        st.session_state.user_data = []

    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    if "user_theme" not in st.session_state:
        st.session_state.user_them = "밝은 테마"

    if "item" not in st.session_state:
        st.session_state.items = [
            {"id":1,"이름":"샘플1","값":150,"상태":"활성"},
            {"id":2,"이름":"샘플2","값":250,"상태":"비활성"},
        ]

initialize_session_state()

tab1, tab2=st.tabs(["세션 상태", "폼 처리"])

with tab1:
    st.subheader("카운터 예제")
    st.write(f"현재 카운터 값: {st.session_state.counter}")

    col1, col2=st.columns(2)

    with col1:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("증가", key="inc"):
                st.session_state.counter+=1
                st.rerun() #streamlit이 가지고 있는 갱신된 값을 웹 페이지로 보낸다

        with col_b:
            if st.button("감소", key="dec"):
                st.session_state.counter-=1
                st.rerun()

        with col_c:
            if st.button("초기화", key="reset"):
                st.session_state.counter = 0
                st.rerun()

    with col2:
        st.subheader("사용자 설정")

        name=st.text_input("이름", value=st.session_state.user_name, key="name_input")
        theme=st.selectbox(
            "테마 선택",
            ["밝은 테마","어두운 테마"],
            index = 0 if st.session_state.user_name == "밝은 테마" else 1
        )

        if st.button("설정 저장"):
            st.session_state.user_name=name
            st.session_state.user_theme=theme
            st.success(f"{name}님의 설정이 저장되었습니다, 테마: {theme}")