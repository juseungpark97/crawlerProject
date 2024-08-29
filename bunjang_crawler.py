import time
import sqlite3
import telepot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 텔레그램 설정 ************************************************************
token = ""  # 텔레그램 Bot 토큰
bot = telepot.Bot(token)  # 텔레그램 봇 객체를 생성합니다.
Bot_ID = ''  # 텔레그램 메시지 수신자 ID

# 텔레그램 메시지 전송 함수
def Sendmsg(msg):
    try:
        bot.sendMessage(Bot_ID, msg, parse_mode='html')  # 메시지를 HTML 포맷으로 전송합니다.
        print(f"텔레그램 메시지 전송: {msg}")  # 메시지 전송 로그
    except Exception as e:
        print(f"텔레그램 오류 발생: {e}")  # 메시지 전송 중 오류가 발생할 경우 오류 메시지를 출력합니다.

# 신규 데이터 DB 저장 함수 (ID만 저장)
def DatatoSQL(item_id):
    with sqlite3.connect("bunjang_crawler.db") as con:
        con.execute("CREATE TABLE IF NOT EXISTS ITEM (ID TEXT PRIMARY KEY)")  # 테이블이 없으면 생성
        con.execute("INSERT OR IGNORE INTO ITEM (ID) VALUES (?)", (item_id,))  # ID 중복시 무시하고 삽입

# 이전에 저장한 DB에서 기존 데이터 확인 (ID만 체크)
def Check():
    with sqlite3.connect("bunjang_crawler.db") as con:
        con.execute("CREATE TABLE IF NOT EXISTS ITEM (ID TEXT PRIMARY KEY)")  # 테이블이 없으면 생성
        return set(row[0] for row in con.execute("SELECT ID FROM ITEM"))  # ID만 가져와서 집합(set)으로 반환

# 웹 드라이버 초기화 함수
def reset_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1920,1080')
    options.add_argument('--incognito')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 번개장터에서 키워드를 검색하고 데이터 수집
def bunjang_search(keyword_search, driver, filter_keywords, first_search=True, max_pages=5):
    existing_ids = Check()

    for page in range(1, max_pages + 1):
        search_url = f"https://m.bunjang.co.kr/search/products?q={keyword_search}&order=date&page={page}"
        driver.get(search_url)
        
        # 페이지 로딩 완료를 기다림
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'sc-kcDeIU.WTgwo'))
        )

        for item in items:
            try:
                # 광고 요소를 무시
                if "sc-iIHSe.bMxODi" in item.get_attribute("class"):
                    continue

                try:
                    title = WebDriverWait(item, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'sc-RcBXQ.kWzERy'))
                    ).text.strip()
                except Exception:
                    # 해당 요소가 없으면 오류를 무시하고 다음으로 진행
                    continue
                
                price = item.find_element(By.CLASS_NAME, 'sc-iSDuPN.cPlkrx').text.strip()
                region = item.find_element(By.CLASS_NAME, 'sc-fZwumE.hFuucq').text.strip()
                link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                item_id = item.find_element(By.TAG_NAME, 'a').get_attribute('data-pid')

                if item_id not in existing_ids:
                    # 새로운 데이터의 ID를 DB에 저장
                    DatatoSQL(item_id)
                    existing_ids.add(item_id)  # 중복 체크를 위해 새로운 ID를 추가

                    # 첫 번째 실행이 아닐 때만 메시지를 보냄
                    if first_search and any(keyword.lower() in title.lower() for keyword in filter_keywords):
                        msg = f"\n{title}\n\n<b>{price}</b>\n\n{region}\n{link}"
                        Sendmsg(msg)
                        time.sleep(3)  # 메시지 전송 후 잠시 대기

            except Exception as e:
                print(f"항목 처리 중 오류 발생: {e}")
                driver.save_screenshot("error_screenshot.png")  # 오류 발생 시 스크린샷 저장

if __name__ == '__main__':
    driver = reset_driver()
    cycle = 1  # 초기 사이클 설정
    filter_keywords = ['14', 'pro', 'M1']  # 필터링할 키워드를 여기에 추가합니다.

    while True:
        try:
            first_search = cycle > 0  # 첫 번째 사이클에서는 메시지를 보내지 않음
            bunjang_search('맥북', driver, filter_keywords, first_search=first_search, max_pages=5)
            cycle += 1  # 사이클 증가
            print(f"cycle {cycle}회 완료")
        except Exception as e:
            print(f"예상하지 못한 오류 발생: {e}")
        finally:
            time.sleep(5)
