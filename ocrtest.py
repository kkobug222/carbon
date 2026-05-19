import easyocr
import re
import sqlite3
import os
import warnings

def init_db():
    #db와 연결하기
    con = sqlite3.connect('food.db')
    cur = con.cursor()
    # print("db 생성 및 연결")

    #테이블 생성
    cur.execute("DROP TABLE IF EXISTS food")
    sql = "CREATE TABLE IF NOT EXISTS food (id int, name varchar(255), co2 float)"
    cur.execute(sql)
    # print("테이블 생성")

    #데이터 추가(txt파일)
    f = open("carbonData.txt", "r", encoding="utf-8")

    for line in f:
        data = line.split()

        id = int(data[0])
        name = data[1]
        co2 = float(data[2])

        sql = "INSERT INTO food VALUES(?, ?, ?)"
        val = (id, name, co2)

        cur.execute(sql, val)
        # print(cur.rowcount,"개 데이터 추가")

    f.close()

    con.commit()
    # print("데이터가 추가됨")

    cur.close()
    con.close()
    # print("db 세팅완료")

#db 조회 함수
def search_food(name):
    file_path = "carbonData.txt" 
    
    # 공백제거
    clean_name = name.replace(" ", "")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "," in line:
                    food_name, co2_val = line.strip().split(",")
                    
                    clean_food_name = food_name.replace(" ", "")
                    
                    #글자 비교 (공백 제거)
                    if clean_food_name in clean_name or clean_name in clean_food_name:
                        print(f"🔍 매칭 성공: {food_name} (탄소량: {co2_val})")
                        return float(co2_val)
                        
    except FileNotFoundError:
        print(f"❌ '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요!")
        
    return -1.0  #품목에 없으면 -1을 출력해서 구분하기

#에러 방지
os.environ["TORCH_SHOW_CPP_STACKTRACES"] = "0"
warnings.filterwarnings("ignore", category=UserWarning)

print("OCR 리더기를 초기화 중입니다...")

reader = easyocr.Reader(['ko', 'en'], gpu=False)
result = reader.readtext('test.webp')  #이미지 파일 넣기!!!!

# 제외 목록
trash_keywords = [
    '주문', '합계', '금액', '매장', 'VAT', '결제취소', '카드', '현금',
    '번호', '메뉴', '수량', '단가', '추가', '제품', '일시', '할인','신용','모바일',
    '결제', '바코드'
]

menu_list = []

print("--- [필터링된 메뉴명 후보] ---")

for detection in result:
    bbox = detection[0]
    text = detection[1].strip()
    prob = detection[2]
    
    # 정확도 별로인 거 버리기
    if prob < 0.4:
        continue
        
    #공백을 제거한 텍스트가 순수 숫자나 기호로만 되어 있으면 패스
    clean_text = re.sub(r'[0-9\s,.\-:/]', '', text)
    if len(clean_text) == 0:
        continue
        
    #제외 키워드가 포함 패스
    if any(keyword in text for keyword in trash_keywords):
        continue
        
    #너무 짧은 이름 없애기
    if len(text) < 2:
        continue

    # 저장
    menu_list.append(text)
    print(f"- {text}")

    co2_val = search_food(text)  # 1. 방금 OCR이 읽은 text를 DB 함수로 보내서 검색하기
    print(f"- {text} : {co2_val}g CO2")  # 2. 메뉴명과 검색된 탄소량을 세트로 출력하기





