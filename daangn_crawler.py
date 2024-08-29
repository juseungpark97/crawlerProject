import time
import pandas as pd
import sqlite3
import telepot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telepot.exception import TelegramError
from urllib3.exceptions import ReadTimeoutError, ProtocolError
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

# 텔레그램 설정 ************************************************************
token = ""  # 텔레그램 Bot 토큰
bot = telepot.Bot(token)  # 텔레그램 봇 객체를 생성합니다.
Bot_ID = ''  # 텔레그램 메시지 수신자 ID

# 텔레그램 메시지 전송 함수
def Sendmsg(msg):
    try:
        bot.sendMessage(Bot_ID, msg, parse_mode='html')  # 메시지를 HTML 포맷으로 전송합니다.
    except TelegramError as e:
        print(f"텔레그램 오류 발생: {e}")  # 메시지 전송 중 오류가 발생할 경우 오류 메시지를 출력합니다.

# 신규 데이터 DB 저장 함수
def DatatoSQL(df):
    with sqlite3.connect("daangn_crawler.db") as con:  # SQLite 데이터베이스와 연결을 엽니다.
        df.to_sql('ITEM', con, if_exists='append', index=False)  # 데이터를 'ITEM' 테이블에 추가합니다.

# 이전에 저장한 DB에서 기존 데이터 확인
def Check():
    try:
        with sqlite3.connect("daangn_crawler.db") as con:  # SQLite 데이터베이스와 연결을 엽니다.
            return pd.read_sql("SELECT ID FROM ITEM", con)['ID'].tolist()  # 'ITEM' 테이블에서 ID 열을 가져와 리스트로 반환합니다.
    except Exception:
        return []  # 예외가 발생하면 빈 리스트를 반환합니다.

# 웹 드라이버 초기화 함수
def reset_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920,1080')  # 브라우저 창 크기를 1920x1080으로 설정합니다.
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())  # 크롬 드라이버 매니저를 통해 최신 드라이버를 설치합니다.
    return webdriver.Chrome(service=service, options=options)  # 설정된 옵션으로 크롬 웹 드라이버를 반환합니다.

# 당근마켓에서 키워드를 검색하고 데이터 수집
def search(keyword_search, driver, filter_keywords, more_clicks=3, first_search=True):
    # 수집할 데이터를 저장할 딕셔너리를 초기화합니다.
    data = {'Title': [], 'Price': [], 'Link': [], 'ID': [], 'Region': []}
    
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

        # '더보기' 버튼을 지정한 횟수만큼 클릭, 클릭 후 버튼이 다시 나타날 때까지 대기
        for _ in range(more_clicks):
            try:
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="result"]/div[1]/div[2]'))
                )
                more_button.click()  # '더보기' 버튼 클릭
                time.sleep(3)

                # '더보기' 버튼이 다시 로드될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="result"]/div[1]/div[2]'))
                )

            except NoSuchElementException:
                print("더보기 버튼을 찾을 수 없습니다.")
                break

        # 검색 결과에서 데이터 추출
        titles = driver.find_elements(By.CLASS_NAME, 'article-title')  # 상품 제목 요소를 모두 찾습니다.
        prices = driver.find_elements(By.CLASS_NAME, 'article-price')  # 상품 가격 요소를 모두 찾습니다.
        regions = driver.find_elements(By.CLASS_NAME, 'article-region-name')  # 지역 정보를 모두 찾습니다.
        links = driver.find_elements(By.CLASS_NAME, 'flea-market-article-link')  # 상품 링크를 모두 찾습니다.
        
        # 각 검색 결과에서 데이터를 추출하여 딕셔너리에 추가합니다.
        for i in range(len(titles)):
            if 'story-article' not in titles[i].get_attribute('class'):  # 광고나 기타 게시물을 제외하기 위한 조건입니다.
                data['Title'].append(titles[i].text.strip())  # 제목을 저장합니다.
                data['Price'].append(prices[i].text.strip() if prices[i].text.strip() else '가격없음')  # 가격이 없으면 '가격없음'으로 저장합니다.
                data['Region'].append(regions[i].text.strip())  # 지역 정보를 저장합니다.
                data['Link'].append(links[i].get_attribute("href"))  # 링크를 저장합니다.

        # 링크에서 ID를 추출하여 저장합니다.
        data['ID'] = [i.split('/')[-1] for i in data['Link']]

        # 기존 DB와 비교하여 새로운 데이터만 처리
        check_list = Check()  # 기존 DB에 저장된 ID를 가져옵니다.
        new_data = pd.DataFrame(data)  # 수집한 데이터를 데이터프레임으로 변환합니다.
        new_items = new_data[~new_data['ID'].isin(check_list)]  # 기존 DB에 없는 새로운 데이터를 필터링합니다.
        
        if not new_items.empty:
            DatatoSQL(new_items)  # 새로운 데이터를 DB에 저장합니다.

            # 새로운 데이터 중 조건에 맞는 항목에 대해 텔레그램 메시지를 보냅니다.
            if first_search:
                for _, row in new_items.iterrows():
                    msg = f"\n{row['Title']}\n\n<b>{row['Price']}</b>\n\n{row['Region']}\n{row['Link']}"  # 메시지 내용을 구성합니다.
                    print(msg)  # 메시지를 콘솔에 출력합니다.

                    if any(keyword.lower() in row['Title'].lower() for keyword in filter_keywords):  # 제목에 필터 키워드가 포함되어 있는지 확인
                        Sendmsg(msg)  # 조건에 맞는 경우 텔레그램 메시지를 전송합니다.
                        time.sleep(3)  # 메시지 전송 후 잠시 대기합니다.

    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")  # 데이터 수집 중 오류가 발생할 경우 오류 메시지를 출력합니다.

# 메인 실행 루프
if __name__ == '__main__':
    cycle = 0
    filter_keywords = ['14', 'pro', 'M1']  # 필터링할 키워드를 여기에 추가합니다.

    driver = reset_driver()  # 웹 드라이버를 초기화합니다.

    while True:
        try:
            first_search = cycle > 0
            search('맥북', driver, filter_keywords, more_clicks=20 ,first_search=first_search)  # '아이폰'이라는 키워드로 검색을 수행합니다.
            cycle += 1
            print("cycle " + str(cycle) + "회 완료")
        except (WebDriverException, TimeoutException):
            print("드라이버 오류 발생. 드라이버를 재설정합니다.")  # 드라이버 오류가 발생할 경우 드라이버를 재설정합니다.
            driver.quit()  # 기존 드라이버를 종료합니다.
            driver = reset_driver()  # 새 드라이버를 초기화합니다.
        except (ConnectionResetError, ConnectionAbortedError, ProtocolError, ReadTimeoutError):
            print("서버 문제로 재시도합니다.")  # 서버 문제로 인한 오류 발생 시 재시도를 알립니다.
        except Exception as e:
            print(f"예상하지 못한 오류 발생: {e}")  
        finally:
            time.sleep(10)  # x초후에 다시 작동합니다.
