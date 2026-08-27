import sqlite3

DB_PATH = r"D:\HomestayERP\database\homestaypj.db"

# 1. 新增訂房
def add_booking(customer_id, room_type_id, checkin, checkout, guest_count, note):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Booking (CustomerId, RoomTypeId, CheckInDate, CheckOutDate, GuestCount, Status, Note)
        VALUES (?, ?, ?, ?, ?, '已確認', ?)
    """, (customer_id, room_type_id, checkin, checkout, guest_count, note))

    conn.commit()
    conn.close()


# 2. 取得所有訂房（這裡用 SQL JOIN 把客戶名字和房型名字一起撈出來，這樣畫面才好看！）
def get_all_bookings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            b.BookingId,
            c.CustomerName,
            r.RoomName,
            b.CheckInDate,
            b.CheckOutDate,
            b.GuestCount,
            b.note
        FROM Booking b
        JOIN Customer c ON b.CustomerId = c.CustomerId
        JOIN RoomType r ON b.RoomTypeId = r.RoomTypeId
    """)
    bookings = cursor.fetchall()
    
    conn.close()
    return bookings

# 3. 根據 ID 刪除特定的訂房紀錄
def delete_booking(booking_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Booking WHERE BookingId = ?", (booking_id,))
    
    conn.commit()
    conn.close()

