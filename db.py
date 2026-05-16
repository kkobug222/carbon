import sqlite3 #모듈 불러오기

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
    con = sqlite3.connect('food.db')
    cur = con.cursor()

    sql = "SELECT * FROM food WHERE name = ?"
    cur.execute(sql, (name,))

    result = cur.fetchall() #조회한 데이터 result 변수에 저장
    for row in result:
        co2 = row[2]

    cur.close()
    con.close()

    return co2