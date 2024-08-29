# Shopping Market Crawler

**Shopping Market Web Crawler v1.0**

**개발 기간**: 2024.08 ~ 2024.09

## 버전 정보

- **Python**: 3.x

- **라이브러리**:
  - **Telepot**: 12.7  
    [다운로드 링크](https://pypi.org/project/telepot/)
  - **Selenium**: 4.5.0  
    [다운로드 링크](https://pypi.org/project/selenium/)
  - **Pandas**: 1.5.0  
    [다운로드 링크](https://pypi.org/project/pandas/)
  - **SQLite3**: Python 기본 라이브러리

## 프로젝트 소개

**Daangn Market Crawler**는 당근마켓 웹사이트에서 특정 키워드를 검색하고, 새롭게 등록된 상품을 자동으로 수집하여 데이터베이스에 저장한 후 텔레그램을 통해 사용자에게 알림을 전송하는 웹 크롤러입니다.

### 주요 기능

- **데이터 수집**: 당근마켓에서 사용자가 지정한 키워드에 대해 검색하고 상품 정보를 수집합니다.
- **DB 저장**: 새롭게 수집된 데이터를 SQLite 데이터베이스에 저장합니다.
- **텔레그램 알림**: 새로운 상품이 등록될 때 텔레그램을 통해 사용자에게 알림을 전송합니다.

### 사용된 기술 스택

- **프로그래밍 언어**:
  - ![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
- **프레임워크 및 라이브러리**:
  - ![Telepot](https://img.shields.io/badge/Telepot-12.7-blue?style=flat-square)
  - ![Selenium](https://img.shields.io/badge/Selenium-4.5.0-green?style=flat-square)
  - ![Pandas](https://img.shields.io/badge/Pandas-1.5.0-orange?style=flat-square)
- **데이터베이스**:
  - ![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=flat-square)
- **API**:
  - ![Telegram API](https://img.shields.io/badge/Telegram%20API-active-green?style=flat-square)

## 프로젝트 설정 및 실행 방법

### 프로젝트 Import

**필수 라이브러리 설치**:
   ```bash
   pip install telepot selenium pandas
   ```

### 코드 예시

```python
# 텔레그램 메시지 전송 함수
def Sendmsg(msg):
    try:
        bot.sendMessage(Bot_ID, msg, parse_mode='html')
    except TelegramError as e:
        print(f"텔레그램 오류 발생: {e}")

# 신규 데이터 DB 저장 함수
def DatatoSQL(df):
    with sqlite3.connect("daangn_crawler.db") as con:
        df.to_sql('ITEM', con, if_exists='append', index=False)

# 이전에 저장한 DB에서 기존 데이터 확인
def Check():
    try:
        with sqlite3.connect("daangn_crawler.db") as con:
            return pd.read_sql("SELECT ID FROM ITEM", con)['ID'].tolist()
    except Exception:
        return []

# 웹 드라이버 초기화 함수
def reset_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920,1080')
    options.add_argument('--incognito')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 당근마켓 접속
    driver.get("https://www.daangn.com/")  # 당근마켓 메인 페이지로 이동합니다.
    
    # 검색어 입력
    try:
        # 검색 창이 로드될 때까지 기다립니다.
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, '_1knjz49a'))  # 검색 창의 클래스 이름을 이용해 요소를 찾습니다.
        )
        elem.send_keys(keyword_search)  # 검색어를 입력합니다.
        elem.send_keys(Keys.RETURN)  # Enter 키를 눌러 검색을 실행합니다.
        
        # 검색 결과가 로드될 때까지 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'flea-market-article-link'))  # 검색 결과 링크가 나타날 때까지 대기합니다.
        )
```
### 코드 주요 기능
- **텔레그램 메시지 전송**: Telepot 라이브러리를 사용하여 텔레그램으로 메시지 전송.
- **웹 드라이버 설정**: Selenium을 사용하여 웹 드라이버 초기화 및 키워드 검색.
- **데이터베이스 처리**: SQLite3 라이브러리를 사용하여 데이터 저장 및 기존 데이터 조회.



