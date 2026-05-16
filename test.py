from flask import Flask, request, render_template
import db

db.init_db()
app = Flask(__name__) #Flask 웹 서버 객체 생성, __name__이 현재 파이썬 파일 이름 정보 전달

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/food")
def food():
    name = request.args.get("name") #js로 보낸 url 읽기 (?name=)부분
    co2 = db.search_food(name)
    return f"오늘 한끼 식사로 {co2}kgCO2의 온실가스를 배출"


# 이 파일에서 실행된 경우 디버그 모드 킴
if __name__ == "__main__":
    app.debug = True
    app.run()
