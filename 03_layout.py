import streamlit as st
import pandas as pd
import numpy as np

st.title("UI 레이아웃 실습")

st.sidebar.title("레이아웃 설정")
layout_type=st.sidebar.selectbox(
    "레이아웃 유형 선택:",
    ["기본 컬럼", "비율 컬럼", "중첩 컬럼"]
)

@st.cache_data #캐싱을 해두고 세션 내에서 계속 쓰겠다
def generate_sample_data():
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = {
        'date': dates,
        'sales': np.random.randint(100, 1000, 30),
        'profit': np.random.randint(10, 100, 30),
        'customers': np.random.randint(50, 200, 30)
    }
    return pd.DataFrame(data)

df = generate_sample_data()

if layout_type == "기본 컬럼":
    st.header("기본 컬럼 레이아웃")
    col1,col2 = st.columns(2)#화면 비율 1대1로 정확히 가져가게 됨

    with col1:
        st.metric("총 매출", f"${df['sales'].sum():,}", "12%")

    with col2:
        st.metric("평균 이익", f"${df['profit'].mean():.0f}", "5%")

elif layout_type=="비율 컬럼":
    col1,col2 = st.columns([2,1])#화면 비율 2대1

    with col1:
        st.bar_chart(df.set_index("date")['profit'])

    with col2:
        st.line_chart(df.set_index("date")['customers'])

elif layout_type=="중첩 컬럼":
    left_col, right_col=st.columns([3,2])

    with left_col:
        sub_col1,sub_col2=st.columns(2)
        with sub_col1:
            st.area_chart(df.set_index("date")["sales"])
        with sub_col2:
            st.bar_chart(df.set_index("date")["profit"])

    with right_col:
        st.write("사이드 영역")
        st.metric("최고 매출", f"${df['sales'].max():,}")