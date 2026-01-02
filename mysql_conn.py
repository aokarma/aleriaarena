import pymysql

connection = pymysql.connect(
    host="localhost",
    user="oko",
    password="Ktpdus7k!",
    database="prestashop",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

print("Połączono z MySQL!")
