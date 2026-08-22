import sqlite3

conn = sqlite3.connect("../../database/homestaypj.db")

with open("../../database/schema.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

conn.executescript(sql_script)

conn.commit()
conn.close()

print("資料庫建立成功")