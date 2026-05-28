from flask import Flask, request, render_template, jsonify
import easyocr
import re
import sqlite3
import os
import warnings

app = Flask(__name__)

# 파일 업로드를 위한 임시 폴더 설정
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# db 초기화
def init_db():
    con = sqlite3.connect('food.db')
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS food")
    cur.execute("CREATE TABLE IF NOT EXISTS food (id int, name varchar(255), co2 float)")

    file_path = "carbonData.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = line.split()
                if len(data) >= 3:
                    try:
                        id_val = int(data[0])
                        name_val = data[1]
                        co2_val = float(data[2])
                        cur.execute("INSERT INTO food VALUES(?, ?, ?)", (id_val, name_val, co2_val))
                    except ValueError:
                        continue
        con.commit()
        print("💡 [DB] carbonData.txt 기반 SQLite 데이터베이스 구축 완료!")
    else:
        print(f"⚠ '{file_path}' 파일이 없습니다. 경로를 확인해주세요.")
    cur.close()
    con.close()

# DB 검색 함수 (공백 제거 후 부분 일치 비교)
def search_food_db(name):
    con = sqlite3.connect('food.db')
    cur = con.cursor()
    
    clean_name = name.replace(" ", "").lower()
    
    cur.execute("SELECT name, co2 FROM food")
    rows = cur.fetchall()
    cur.close()
    con.close()
    
    for food_name, co2_val in rows:
        clean_food_name = food_name.replace(" ", "").lower()
        if clean_food_name in clean_name or clean_name in clean_food_name:
            return float(co2_val)
            
    return -1.0

# 서버 기동 시 DB 초기 세팅
init_db()

# 전역 공간에서 EasyOCR 리더기 로드
print("⚙️ EasyOCR 리더기 초기화 중 (시간이 다소 소요될 수 있습니다)...")
reader = easyocr.Reader(['ko', 'en'], gpu=False)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-receipt', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "업로드된 파일이 없습니다."}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다."}), 400

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:

            con = sqlite3.connect('food.db')
            cur = con.cursor()
            cur.execute("SELECT name, co2 FROM food")
            all_rows = cur.fetchall()
            cur.close()
            con.close()
            all_food_db = {row[0]: row[1] for row in all_rows}

            # EasyOCR 실행 및 분석
            result = reader.readtext(file_path)
            
            trash_keywords = [
                '주문', '합계', '금액', '매장', 'VAT', '결제취소', '카드', '현금',
                '번호', '메뉴', '수량', '단가', '추가', '제품', '일시', '할인','신용','모바일',
                '결제', '바코드', 'subtotal', 'total', 'tax', 'tip', 'receipt'
            ]

            detected_menu_db = {}

            for detection in result:
                text = detection[1].strip()
                prob = detection[2]
                
                if prob < 0.4: continue
                
                clean_text = re.sub(r'[0-9\s,.\-:/$]', '', text)
                if len(clean_text) == 0: continue
                if any(keyword in text.lower() for keyword in trash_keywords): continue
                if len(text) < 2: continue

                co2_val = search_food_db(text)
                if co2_val != -1.0:
                    detected_menu_db[text] = co2_val

            if os.path.exists(file_path):
                os.remove(file_path)

            is_fallback_flag = False

            # 만약 영수증 인식에 실패해서 결과 딕셔너리가 비어있다면 전체 메뉴 서빙
            if not detected_menu_db:
                is_fallback_flag = True
                
                con = sqlite3.connect('food.db')
                cur = con.cursor()
                cur.execute("SELECT name, co2 FROM food")
                rows = cur.fetchall()
                cur.close()
                con.close()
                
                detected_menu_db = {row[0]: row[1] for row in rows}

            return jsonify({
                "success": True, 
                "db": detected_menu_db,
                "all_db": all_food_db,
                "is_fallback": is_fallback_flag
            })

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": f"서버 처리 오류: {str(e)}"}), 500

if __name__ == '__main__':
    os.environ["TORCH_SHOW_CPP_STACKTRACES"] = "0"
    warnings.filterwarnings("ignore", category=UserWarning)
    app.run(debug=True, port=5000)