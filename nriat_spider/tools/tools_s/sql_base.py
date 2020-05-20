import pymysql
def get_data(sql_prame,sql):
    connect = pymysql.connect(host=sql_prame.get("host"), port=3306, db=sql_prame.get("db"),
                               user=sql_prame.get("user"), password=sql_prame.get("password"), charset="utf8",
                               use_unicode=True, cursorclass=pymysql.cursors.Cursor)
    cursor = connect.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    connect.close()
    return data


def get_bigdata(sql_prame,sql):
    connect = pymysql.connect(host=sql_prame.get("host"), port=3306, db=sql_prame.get("db"),
                               user=sql_prame.get("user"), password=sql_prame.get("password"), charset="utf8",
                               use_unicode=True, cursorclass=pymysql.cursors.SSCursor)
    cursor = connect.cursor()
    cursor.execute(sql)
    while True:
        one = cursor.fetchone()
        if not one:
            break
        yield one
    cursor.close()
    connect.close()

if __name__=="__main__":
    sql = '''select shop_id,company,sales_count,sales_money,shop_name,city,county
from tmall_shopinfo_201912 limit 100'''
    sql_prame = {
        "host": "192.168.0.228",
        "db": "e_commerce",
        "user": "dev",
        "password": "Data227or8Dev715#"
    }
    sql_input = (sql_prame,sql)
    for i in get_bigdata(sql_prame,sql):
        a = i










