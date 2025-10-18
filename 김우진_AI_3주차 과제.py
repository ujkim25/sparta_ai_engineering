import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime

st.set_page_config(page_title="한국어 감정 분석", layout="wide")

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained("rkdaldus/ko-sent5-classification")
    # 둘 다 허깅페이스에 올라와있는 tokenizer와 model
    return tokenizer, model

def analyze_sentiment(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    # 입력 텍스트를 모델이 이해할 수 있는 숫자 형태로 변환하는 단계
    # tokenizer: 문장을 단어 단위로 자르고 숫자로 바꿔주는 도구
    # return_tensors="pt": PyTorch 텐서(torch.Tensor) 형태로 리턴하라는 뜻
    # input_ids : 각 단어를 숫자로 바꾼 결과 (문장 내용)
    with torch.no_grad():
        outputs = model(**inputs)
        # 모델에 입력을 넣어 예측(logits) 을 얻는 단계
        # **를 쓰면 딕셔너리였던 inputs가 input_ids=... , token_type_ids=..., attention_mask=... 형태로 자동 전달
        # logits는 모델이 각 감정 클래스에 대해 얼마나 "그쪽일 확률이 높다고 생각하는지" 나타내는 점수
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    # torch.argmax(tensor, dim=1) : 각 행에서 가장 큰 값의 인덱스를 반환
    # 이 결과는 텐서이므로 .item()으로 파이썬 숫자로

    emoticon_labels={
        0:"Angry",
        1:"Fear",
        2:"Happy",
        3:"Tender",
        4:"Sad"
    }

    return emoticon_labels[predicted_label]

if 'history' not in st.session_state:
    st.session_state.history = []

with st.spinner('모델을 로딩중입니다...'):
    tokenizer, model = load_model()

st.title("한국어 감정 분석 앱")
st.markdown("---")

left_col,right_col = st.columns([2,1])

with left_col:
    st.subheader("감정 입력")
    text_area = st.text_area("감정을 표현하는 문장을 입력하세요:", height=100)

if st.button("감정 분석하기"):
    if not text_area.strip():
        st.warning("감정을 입력하세요!")
    else:
        with st.spinner('감정을 분석중입니다...'):
            emotion = analyze_sentiment(text_area, tokenizer, model)
        st.write(f"감정: {emotion}")
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.write(f"분석 시간: {time}")
        st.session_state.history.insert(0,{
            "입력": text_area,
            "감정": emotion,
            "시간": time
        })

with right_col:
    st.subheader("분석 기록")
    if st.button("기록 초기화"):
        st.session_state.history = []
        st.rerun()
    if len(st.session_state.history) == 0:
        st.write("아직 분석 기록이 없습니다.")
    else:
        for analysis in st.session_state.history:
            st.write(f"입력 문장: {analysis["입력"]}")
            st.write(f"예측 감정: {analysis["감정"]}")
            st.write(f"분석 시간: {analysis["시간"]}")
            st.markdown("---")

st.markdown("---")
st.title("텍스트 생성 스트리밍")

import time

def text_generator():
    """텍스트를 한 단어씩 생성하는 generator 함수"""
    sample_text = """
다시 시작되는 월요일에게 붙이는 짧은 시

커피가 먼저 부팅되고, 내가 뒤늦게 로그인한다.
알람은 세 번의 재시도를 거쳐 나를 인증한다.
거울 속 내 얼굴은 “쿠키 허용?”을 묻는다.

현관 앞 양말은 좌우가 다르다—A/B 테스트 중이라서.
엘리베이터는 1층에서만 고집 세고,
나는 계단에서 숨이 차 “업데이트 나중에”를 누른다.

회사 앞 자판기는 잔액을 모른 척하고,
내 지갑은 오류 메시지 없이 비었다.
점심 메뉴는 회의록보다 길고, 결정은 더 느리다.

그래도 퇴근길 하늘이 파랗게 컴파일되면
나는 하루를 저장하고—이불 속에서
어제에 Ctrl+Z, 내일에 Ctrl+S를 누른다.
"""

    words = sample_text.split()

    for word in words:
        yield word + " "
        # yield로 한 단어씩 리턴
        # 멈췄다가 이어서 실행 가능
        # 여러 값을 순차적으로 “흘려보냄”
        time.sleep(0.05)

question = st.text_input("질문을 입력하세요:")
if st.button("AI 응답 생성"):
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write_stream(text_generator)
        # 함수 자체(=생성자)를 넘김 → Streamlit이 알아서 호출함
        st.success("응답 완료")