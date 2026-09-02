import sqlite3
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../../../database/homestaypj.db"))
if not os.path.exists("D:\\"):
    DB_PATH = "/tmp/homestaypj.db"

#  customer.py 定義的絕對路徑
# DB_PATH = r"D:\HomestayERP\database\homestaypj.db"

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

# 3. 查詢指定日期區間的剩餘空房
def check_available_rooms(start_date, end_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 這個 SQL 會撈出所有房型，並計算在該日期區間內，已經被預訂的房間數量
    cursor.execute("""
        SELECT 
            r.RoomTypeId,
            r.RoomName,
            r.Capacity,
            r.TotalRooms,
            COUNT(b.BookingId) AS BookedRooms,
            (r.TotalRooms - COUNT(b.BookingId)) AS AvailableRooms
        FROM RoomType r
        LEFT JOIN Booking b ON r.RoomTypeId = b.RoomTypeId
            AND b.Status = '已確認'
            AND NOT (b.CheckOutDate <= ? OR b.CheckInDate >= ?)
        GROUP BY r.RoomTypeId
    """, (start_date, end_date))
    
    available_rooms = cursor.fetchall()
    conn.close()
    return available_rooms
