import easyocr
import re

reader = easyocr.Reader(['ko', 'en'], gpu=False)
result = reader.readtext('test.webp')  #이미지 파일명

# 1. 영수증에서 제외할 키워드 목록 (가게 정보, 결제 정보 등)
trash_keywords = [
    '주문', '합계', '금액', '부가세', 'VAT', '결제', '카드', '승인',
    '번호', '메뉴', '수량', '단가', '주소', '대표', '일시', '가게', 'TEL'
]

menu_list = []

print("--- [필터링된 메뉴명 후보] ---")

for detection in result:
    bbox = detection[0]
    text = detection[1].strip()
    prob = detection[2]
    
    # 너무 신뢰도가 낮은 인식 결과는 버림
    if prob < 0.4:
        continue
        
    # 규칙 A: 공백을 제거한 텍스트가 순수 숫자나 기호(천원 단위 쉼표 등)로만 되어 있으면 금액/수량이므로 패스
    clean_text = re.sub(r'[0-9\s,.\-:/]', '', text)
    if len(clean_text) == 0:
        continue
        
    # 규칙 B: 제외 키워드가 포함되어 있다면 영수증 안내 문구이므로 패스
    if any(keyword in text for keyword in trash_keywords):
        continue
        
    # 규칙 C: 메뉴명은 보통 최소 2글자 이상 (글자 수가 너무 짧은 오인식 데이터 제거)
    if len(text) < 2:
        continue

    # 모든 필터를 통과한 텍스트를 메뉴 후보로 저장
    menu_list.append(text)
    print(f"- {text}")