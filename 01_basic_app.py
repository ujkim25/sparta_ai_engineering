import streamlit as st

st.set_page_config(
    page_title="기본 streamlit 앱",
    page_icon="®",
    layout="centered"
)
st.title("첫번째 앱 입니다")
st.write("내 첫번째 streamlit 어플리케이션")

st.divider()

st.header("텍스트 출력 예제")
st.markdown("**굵은 글씨**와 *기울임 글씨* 예제")
st.text("고정폭 폰트로 표시되는 텍스트")

st.subheader("코드 표시")
st.code(
"""
def hello_world():
    print("Hello, Streamlit)
    return "안녕"
""", language="python")

st.header("사용자 입력 예제")

user_name = st.text_input("이름을 입력하세요:")

if user_name:
    st.write(f"안녕하세요, {user_name}님")
    st.success(f"안녕하세요, 환영합니다")

age=st.number_input("나이를 입력하세요",min_value=0,max_value=120,value=25)
st.write(f"입력하신 나이: {age}세")

favorite_color = st.selectbox(
    "좋아하는 색깔?",
    ["빨","파","초"]
)
st.write(f"선택하신 색깔: {favorite_color}")

st.divider()

st.header("버튼 예제")
if st.button("인사하기"):
    st.balloons()
    st.write("축하합니다 버튼을 클릭")

st.info("정보 메시지")
st.warning("경고 메시지")

st.sidebar.title("사이드바")
st.sidebar.write("여기는 사이드바입니다.")
sidebar_option = st.sidebar.radio(
    "옵션을 선택하세요:",
    ["1","2"]
)
st.sidebar.write(f"선택된 옵션: {sidebar_option}")