import os
import streamlit as st
import requests
from openai import OpenAI
from dotenv import load_dotenv
import json
from main import search_news

# 환경변수 로드
load_dotenv()

# FastAPI 서버 URL (환경변수로 설정 가능)
FASTAPI_URL = "http://localhost:8000"

# OpenAI 클라이언트 초기화
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다.")
        return None
    return OpenAI(api_key=api_key)


def get_news_articles(query: str, display: int = 10):
    ################################################
    ######### 필수 과제 - 문제 2: fastapi를 호출한 검색결과 가져오기
    news_articles = search_news(query, display)['articles']

    return news_articles
    ################################################


def generate_with_openai(news_list, prompt):
    
    client = get_openai_client()
    if not client:
        return None
    
    # 뉴스 데이터를 JSON 문자열로 변환
    news_json = json.dumps(news_list, ensure_ascii=False, indent=2)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": news_json}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API 오류: {str(e)}")
        return None
    


def transcribe_audio(audio_file):
    """오디오 파일을 텍스트로 변환 (STT)"""
    client = get_openai_client()
    if not client:
        return None
    
    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcription.text
    except Exception as e:
        st.error(f"STT 오류: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(
    page_title="뉴스 검색 및 분석",
    page_icon="📰",
    layout="wide"
)

st.title("📰 네이버 뉴스 검색 및 AI 분석")

# 탭 생성
tab1, tab2 = st.tabs(["🔍 뉴스 검색 & 분석", "🎤 음성 입력 (STT)"])

with tab1:
    st.header("뉴스 검색")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("검색어를 입력하세요", placeholder="예: 주식, AI, 부동산")
    with col2:
        num_articles = st.number_input("기사 수", min_value=1, max_value=10, value=5)
    
    search_button = st.button("🔍 검색", type="primary", use_container_width=True)
    
    # 세션 스테이트에 뉴스 데이터 저장
    if "news_data" not in st.session_state:
        st.session_state.news_data = []
    
    if search_button and search_query:
        with st.spinner("FastAPI 서버를 통해 뉴스를 검색하고 있습니다..."):
            news_articles = get_news_articles(search_query, num_articles)
            st.session_state.news_data = news_articles
        
        if news_articles:
            st.success(f"✅ {len(news_articles)}개의 뉴스 기사를 찾았습니다!")
        else:
            st.warning("검색 결과가 없습니다.")
    
    # 검색 결과 표시
    if st.session_state.news_data:
        st.header("검색 결과")
        
        ################################################
        ######### 필수 과제 - 문제 3: 검색결과 화면에 st.expander로 표시 및 LLM 프롬프팅 결과 출력        i = 1
        
        for news in st.session_state.news_data:
            with st.expander(f"{news['title']}"):
                st.write(f"링크: {news['link']}")
                st.write(f"본문: {news['text']}")

        st.header("AI 분석 요청")
        text_area = st.text_area("프롬프트를 입력하세요", height=100)
        analyze_button = st.button("AI 분석 실행", type="primary", use_container_width=True)
        if analyze_button:
            with st.spinner("뉴스를 분석하고 있습니다..."):
                analysis = generate_with_openai(st.session_state.news_data, text_area)
                st.header("AI 분석 결과")
                st.write(analysis)

        ################################################
        
with tab2:
    st.header("음성 입력 및 STT (Speech to Text)")
    
    st.info("🎤 마이크 버튼을 눌러 음성을 녹음하세요. 녹음이 끝나면 자동으로 텍스트로 변환됩니다.")
    
    ##################################################
    ######### 도전 과제 - 문제 4: streamlit으로 오디오 입력 기능 구현
    audio_value = st.audio_input("음성 메시지 녹음")

    if audio_value:
        st.markdown("**녹음된 오디오**")
        st.audio(audio_value)
        st.markdown("**텍스트 변환 중...**")
        stt_result = transcribe_audio(audio_value)
        if stt_result != None:
            st.success("변환 완료!")
            st.markdown("**변환된 텍스트**")
            st.write("STT 결과")
            st.code(f"""
            {stt_result}
            """)
            search_with_sst_result = st.button("이 텍스트로 뉴스 검색하기", icon="🎤")
            if search_with_sst_result:
                with st.spinner("FastAPI 서버를 통해 뉴스를 검색하고 있습니다..."):
                    news_articles = get_news_articles(stt_result, 5)
                    st.session_state.news_data = news_articles
                if news_articles:
                    st.success(f"✅ {len(news_articles)}개의 뉴스 기사를 찾았습니다!")
            if st.session_state.news_data:
                for news in st.session_state.news_data:
                    with st.expander(f"{news['title']}"):
                        st.write(f"링크: {news['link']}")
                        st.write(f"본문: {news['text']}")

    ##################################################

