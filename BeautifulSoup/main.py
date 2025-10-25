import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = FastAPI(title="Naver News Search API")


# 응답 모델
class NewsArticle(BaseModel):
    title: str
    link: str
    body: str


class NewsResponse(BaseModel):
    total: int
    articles: List[NewsArticle]


# User Agent 설정
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0 Safari/537.36"
)

session = requests.Session()
session.headers.update({"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})


def extract_naver_article_html(html: str):
    """네이버 뉴스 페이지 전용 파서"""
    soup = BeautifulSoup(html, "lxml")
    # 모바일(mnews)에서 본문
    article = soup.select_one("#dic_area")
    # PC(news)에서 본문
    if not article:
        article = soup.select_one("#newsct_article")
    if not article:
        return None
    # 불필요 요소 제거
    for s in article.select(
        "script, style, .media_end_correction, .copyright, figure"
    ):
        s.decompose()
    for br in article.find_all("br"):
        br.replace_with("\n")
    return article.get_text("\n", strip=True)


def fetch_article_text(url: str, timeout: int = 15):
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except Exception:
        return None

    html = resp.text
    final_url = resp.url

    # 네이버 뉴스 도메인 체크
    if (
        "n.news.naver.com" not in final_url
        and "news.naver.com" not in final_url
    ):
        return None

    # 네이버 뉴스 페이지 전용 파서
    txt2 = extract_naver_article_html(html)
    if txt2 and len(txt2.strip()) > 50:
        return txt2.strip()

    return None


def search_naver_news(query: str, display: int = 10):
    """네이버 뉴스 검색 API 호출"""
    api_key = os.getenv("NAVER_API_KEY")
    secret_key = os.getenv("NAVER_SECRET_KEY")

    if not api_key or not secret_key:
        raise HTTPException(
            status_code=500,
            detail="NAVER_API_KEY or NAVER_SECRET_KEY not found in environment variables",
        )

    url = "https://openapi.naver.com/v1/search/news.json"

    params = {
        "query": query,
        "display": display,
        "start": 1,
        "sort": "sim",
    }

    headers = {
        "X-Naver-Client-Id": api_key,
        "X-Naver-Client-Secret": secret_key,
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        resp.encoding = "utf-8"
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Naver API error: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"message": "Naver News Search API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/search", response_model=NewsResponse)
def search_news(query, display):
    """
    네이버 뉴스 검색 및 본문 추출
    """

    search_result = search_naver_news(query, display)

    if "items" not in search_result:
        raise HTTPException(
            status_code=500, detail="Invalid response from Naver API"
        )

    ################################################
    ######### 필수 과제 - 문제 1: 네이버 뉴스 링크만 필터링
    news_list = []

    for item in search_result['items']:
        news = {}
        if fetch_article_text(item['link']) != None:
            title = item['title']
            if '<b>' in title:
                title = title.replace('<b>','')
            if '</b>' in title:
                title = title.replace('</b>','')
            news['title'] = title
            news['link'] = item['link']
            news['text'] = fetch_article_text(item['link'])
            news_list.append(news)

    """
    new_list의 각 item 예시:
    {
        'title': '잊고 있던 미수령 <b>주식</b> 433억, 주인 찾았다',
        'originallink': 'https://www.newsis.com/view/NISX20251023_0003374173',
        'link': 'https://n.news.naver.com/mnews/article/003/0013553420?sid=101',
        'description': '경기도에 사는 40대 A씨는 오래전 투자했던 비상장 <b>주식</b>의 존재를 잊고 지냈다. ',
        'pubDate': 'Thu, 23 Oct 2025 14:15:00 +0900'
    }
    """

    ################################################

    return {"total": len(news_list), "articles": news_list}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
