import sqlite3
import os

# 動態抓取資料庫絕對路徑
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = CURRENT_DIR.split("backend")[0] # 自動切到 backend 之前的那一層（也就是 HomestayERP）
DB_PATH = os.path.join(BASE_DIR, "database", "homestaypj.db")

def get_all_templates():
    """撈出所有的行程模板列表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT TemplateId, TemplateName FROM Template")
    templates = cursor.fetchall()
    conn.close()
    return templates

def add_template(template_name):
    """新增一個行程模板標題，並回傳剛生成的 TemplateId"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Template (TemplateName) VALUES (?)", (template_name,))
    template_id = cursor.lastrowid # 💡 拿到剛生成的 ID，方便等等塞每日細節
    conn.commit()
    conn.close()
    return template_id

def add_template_detail(template_id, day_number, activity_time, description):
    """幫指定模板塞入每日行程細節"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO TemplateDetail (TemplateId, DayNumber, ActivityTime, Description)
        VALUES (?, ?, ?, ?)
    """, (template_id, day_number, activity_time, description))
    conn.commit()
    conn.close()

def get_template_by_id(template_id):
    """根據 ID 撈出單一模板的資訊"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT TemplateId, TemplateName FROM Template WHERE TemplateId = ?", (template_id,))
    template = cursor.fetchone()
    conn.close()
    return template

def get_template_details(template_id):
    """撈出某個模板的所有每日行程細節，並按照天數與時間排序"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DetailId, DayNumber, ActivityTime, Description 
        FROM TemplateDetail 
        WHERE TemplateId = ?
        ORDER BY DayNumber ASC, ActivityTime ASC
    """, (template_id,))
    details = cursor.fetchall()
    conn.close()
    return details

def delete_template_detail(detail_id):
    """根據明細的 DetailId 刪除該筆行程時段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TemplateDetail WHERE DetailId = ?", (detail_id,))
    conn.commit()
    conn.close()

def delete_entire_template(template_id):
    """刪除整個行程模板，連同底下的所有每日行程細節"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ① 先刪除該模板底下的所有每日細節
    cursor.execute("DELETE FROM TemplateDetail WHERE TemplateId = ?", (template_id,))
    
    # ② 再刪除模板主體本身
    cursor.execute("DELETE FROM Template WHERE TemplateId = ?", (template_id,))
    
    conn.commit()
    conn.close()

def apply_template_to_booking(booking_id, template_id):
    """【主線核心】將指定的行程模板複製一份，正式綁定到該筆訂房訂單上"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ① 先預防性清理：如果這筆訂單之前已經套用過行程，先把它刪掉，避免重複套用塞爆
    cursor.execute("DELETE FROM Itinerary WHERE BookingId = ?", (booking_id,))
    
    # ② 撈出該範本底下的所有每日行程細節
    cursor.execute("""
        SELECT DayNumber, ActivityTime, Description 
        FROM TemplateDetail 
        WHERE TemplateId = ?
    """, (template_id,))
    details = cursor.fetchall()
    
    # ③ 迴圈跑每一筆細節，複製一份，改綁定客人的 BookingId，塞進 Itinerary 表
    for d in details:
        cursor.execute("""
            INSERT INTO Itinerary (BookingId, DayNumber, ActivityTime, Description)
            VALUES (?, ?, ?, ?)
        """, (booking_id, d[0], d[1], d[2]))
        
    conn.commit()
    conn.close()

def get_booking_itinerary(booking_id):
    """撈出某筆訂房訂單目前已經綁定的專屬客製化行程"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ItineraryId, DayNumber, ActivityTime, Description 
        FROM Itinerary 
        WHERE BookingId = ?
        ORDER BY DayNumber ASC, ActivityTime ASC
    """, (booking_id,))
    itinerary_list = cursor.fetchall()
    conn.close()
    return itinerary_list

