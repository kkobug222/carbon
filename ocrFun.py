import easyocr
import re

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

