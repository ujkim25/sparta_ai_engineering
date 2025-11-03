# HTML 파싱을 위한 BeautifulSoup 라이브러리 임포트
from bs4 import BeautifulSoup

# HTML 파일을 UTF-8 인코딩으로 읽기
with open('서울경제.html', 'r', encoding='utf-8') as f:
    html = f.read()

# BeautifulSoup 객체 생성 (html.parser 사용)
soup = BeautifulSoup(html, 'html.parser')

# 추출한 기사들을 저장할 리스트
articles = []

# HTML에서 type1, type2, type3 클래스를 가진 모든 li 태그 찾기 (각각이 하나의 기사)
# class_는 CSS 클래스를 여러 개 검색할 수 있는 함수를 사용
for article in soup.find_all('li', class_=['type1', 'type2', 'type3']):
    # 기사 제목 추출
    # 'list_tit' 클래스를 가진 div 태그에서 제목을 찾음
    title = article.find('div', class_='list_tit')
    if title:
        # get_text()로 텍스트만 추출, strip=True로 앞뒤 공백 제거
        title_text = title.get_text(strip=True)
    else:
        title_text = ''
    
    # 기사 본문 추출
    # 'main_text' 클래스를 가진 div 태그에서 본문을 찾음
    main_text = article.find('div', class_='main_text')
    if main_text:
        # get_text()로 텍스트만 추출, strip=True로 앞뒤 공백 제거
        content = main_text.get_text(strip=True)
    else:
        content = ''
    
    # 제목이나 본문이 있으면 리스트에 추가
    if title_text or content:
        # 제목과 본문을 포맷팅하여 추가 (= 기호 80개로 구분선 생성)
        articles.append(f"[제목] {title_text}\n\n{content}\n\n{'='*80}\n")

# 추출한 기사들을 텍스트 파일로 저장
with open('본문_내용.txt', 'w', encoding='utf-8') as f:
    # 리스트의 모든 기사를 하나의 문자열로 합쳐서 파일에 쓰기
    f.write('\n'.join(articles))

# 결과 출력
print(f"총 {len(articles)}개의 기사 본문을 추출했습니다.")
print("결과가 '본문_내용.txt' 파일에 저장되었습니다.")

