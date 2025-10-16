import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date#, time
import time

tab1, tab2 = st.tabs(["입력 위젯", "데이터표시"])

with tab1:
    st.header("입력 위젯 모음")

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("텍스트 입력")
        text_input=st.text_input("텍스트 입력", placeholder="입력해주세요")
        slider=st.slider("슬라이더 입력",0,100,10)

    with col2:
        st.subheader("선택 위젯")
        multiselect = st.multiselect("다중 선택", ["A","B","C"])

        st.subheader("날짜/시간")
        date_input = st.date_input("날짜 선택", value=date.today())
        # time_input = st.time_input("시간 선택", value=time(12,0))

with tab2:
    st.header("데이터 표시 컴포넌트")
    
    # 샘플 데이터 생성
    df = pd.DataFrame({
        '이름': ['김철수', '이영희', '박민수', '정수진', '최영수'],
        '나이': [25, 30, 35, 28, 32],
        '점수': [85, 92, 78, 95, 88],
        '등급': ['B', 'A', 'C', 'A', 'B']
    })

    st.dataframe(df, use_container_width=True)

st.subheader("지도")
map_data = pd.DataFrame(
    np.random.randn(100, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)

st.map(map_data)

st.header("미디어 컴포넌트")
col1,col2 = st.columns(2)

with col1:
    st.subheader("이미지")
    image_array = np.random.rand(100,100,3) #이미지도 숫자이다
    st.image(image_array, caption="랜덤 이미지", width=200)

    st.subheader("파일 업로드")
    uploaded_file=st.file_uploader(
        "파일을 선택하세요",
        type=['txt','csv']
    )
    if uploaded_file is not None:
        st.write(f"업로드 된 파일:{uploaded_file.name}")
        st.write(f"파일 크기 : {uploaded_file.size}")

with col2:
    st.subheader("다운로드 버튼")
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="csv 다운로드",
        data=csv_data,
        file_name="sample_data.csv",
        mime="text/csv"
    )

    st.subheader("진행률 표시")
    if st.button("진행률 시뮬레이션"): #버튼이 눌렸을 때
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i in range(100):
            time.sleep(1)
            progress_bar.progress(i+1)
            status_text.text(f"진행률:{i+1}%")
        
        status_text.text('완료!')
        st.success('작업이 완료되었습니다!')