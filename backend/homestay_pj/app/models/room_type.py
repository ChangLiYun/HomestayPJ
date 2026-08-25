import sqlite3

# 這裡共用之前在 customer.py 定義的絕對路徑
DB_PATH = r"D:\HomestayERP\database\homestaypj.db"

# 1. 新增房型功能
def add_room_type(room_name, capacity, total_rooms):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO RoomType (RoomName, Capacity, TotalRooms)
        VALUES (?, ?, ?)
    """, (room_name, capacity, total_rooms))
    
    conn.commit()
    conn.close()

# 2. 取得所有房型功能
def get_all_room_types():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM RoomType")
    room_types = cursor.fetchall()
    
    conn.close()
    return room_types
