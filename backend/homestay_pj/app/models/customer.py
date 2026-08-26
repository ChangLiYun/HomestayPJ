import sqlite3

DB_PATH = r"D:\HomestayERP\database\homestaypj.db"

def add_customer(customer_name, phone):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 只寫入資料庫目前確實存在的 CustomerName 和 Phone 欄位
    cursor.execute("""
        INSERT INTO Customer (CustomerName, Phone)
        VALUES (?, ?)
    """, (customer_name, phone))

    conn.commit()
    conn.close()


def get_all_customers():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Customer
    """)

    customers = cursor.fetchall()

    conn.close()

    return customers


# 1. 根據 ID 找到特定的客戶資料（改用你的 DB_PATH 欄位名稱）
def get_customer_by_id(customer_id):
    conn = sqlite3.connect(DB_PATH) # 👈 改用你定義好的 DB_PATH
    cursor = conn.cursor()
    
    # 這裡假設你的主鍵欄位名稱叫 CustomerID，如果資料庫裡是小寫 id，請把它改成 id
    cursor.execute("SELECT * FROM Customer WHERE CustomerID = ?", (customer_id,))
    customer = cursor.fetchone()
    
    conn.close()
    return customer

# 2. 接收新的欄位資料，並更新到資料庫中（只保留 3 個參數：ID、姓名、電話）
def update_customer(customer_id, name, phone):
    conn = sqlite3.connect(DB_PATH) # 使用你最上方定義好的 DB_PATH
    cursor = conn.cursor()
    
    # 這裡只更新資料庫目前確實存在的 CustomerName 和 Phone
    cursor.execute("""
        UPDATE Customer 
        SET CustomerName = ?, Phone = ?
        WHERE CustomerID = ?
    """, (name, phone, customer_id))
    
    conn.commit()
    conn.close()


# 3. 根據 ID 刪除特定的客戶資料
def delete_customer(customer_id):
    conn = sqlite3.connect(DB_PATH) # 這裡同樣使用你定義好的 DB_PATH
    cursor = conn.cursor()
    
    # 執行 SQL 刪除指令
    cursor.execute("DELETE FROM Customer WHERE CustomerID = ?", (customer_id,))
    
    conn.commit()
    conn.close()
