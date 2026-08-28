import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
import io

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

def get_detail_by_id(detail_id):
    """根據明細 ID 撈出單一筆行程時段資料（用於編輯帶入舊資料）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DetailId, TemplateId, DayNumber, ActivityTime, Description FROM TemplateDetail WHERE DetailId = ?", (detail_id,))
    detail = cursor.fetchone()
    conn.close()
    return detail

def update_template_detail(detail_id, day_number, activity_time, description):
    """更新某一筆行程時段，儲存後會因 ORDER BY 自動重新排序位置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE TemplateDetail 
        SET DayNumber = ?, ActivityTime = ?, Description = ? 
        WHERE DetailId = ?
    """, (day_number, activity_time, description, detail_id))
    conn.commit()
    conn.close()

#---- 圖片輸出 ---------------------------------------------------------------------------

def generate_itinerary_jpg(booking_info, itinerary_list):
    """【Pillow 產圖核心】將客人的訂單與行程明細繪製成一張高質感的 JPG 圖片"""
    
    # 1. 創建一個寬 800 像素、高 1200 像素的質感白色畫布（之後也可以用現成的背景圖片 open）
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 2. 繪製一些裝飾線條與色塊，提升質感
    draw.rectangle([0, 0, 800, 120], fill=(230, 247, 255)) # 頂部淡藍色區塊
    
    # 3. 載入中文字型（重要：必須確保系統路徑有該字型，這裡以 Windows 內建微軟正黑體為例）
    # 如果是 Linux/Mac 或沒字型，可以放一個開源的思源黑體 .ttf 到 static/fonts/ 夾裡
    try:
        font_title = ImageFont.truetype("msjh.ttc", 36) # 標題字型
        font_sub = ImageFont.truetype("msjh.ttc", 20)   # 內文字型
        font_bold = ImageFont.truetype("msjh.ttc", 22)  # 粗體內文
    except IOError:
        # 防呆：如果找不到字型，就使用系統預設（不支援中文，僅作不當機防護）
        font_title = font_sub = font_bold = ImageFont.load_default()
        
    # 4. 寫入客人的基本資訊（booking_info 假設是一個 Tuple 或 Dict，對齊你的 get_all_bookings 順序）
    # booking = BookingId, booking = CustomerName, booking = RoomName...
    c_name = booking_info[1]
    r_name = booking_info[2]
    checkin = booking_info[3]
    checkout = booking_info[4]
    
    draw.text((40, 40), "🏨 HomestayPJ 民宿歡迎您", fill=(0, 102, 204), font=font_title)
    
    info_text = f"貴賓：{c_name}  |  預訂房型：{r_name}\n入住區間：{checkin} ～ {checkout}"
    draw.text((40, 150), info_text, fill=(50, 50, 50), font=font_bold)
    
    # 繪製一條分隔線
    draw.line([(40, 220), (760, 220)], fill=(200, 200, 200), width=2)
    
    # 5. 迴圈印出客人的客製化行程明細
    draw.text((40, 240), "🗺️ 您的專屬精選行程規劃：", fill=(0, 102, 204), font=font_bold)
    
    current_y = 290
    for idx, item in enumerate(itinerary_list):
        # 避免行程太多超出底稿，加個防超界
        if current_y > 1120:
            draw.text((40, current_y), "...更多精彩行程現場為您奉上...", fill=(120, 120, 120), font=font_sub)
            break
            
        day_str = f"第 {item[1]} 天"
        time_str = item[2]
        desc_str = item[3]
        
        # 繪製天數標籤與時間
        draw.text((40, current_y), f"[{day_str} {time_str}]", fill=(0, 153, 76), font=font_bold)
        
        # 處理景點描述文字（如果太長，簡單做個截斷或換行，這裡先採截斷防疊字）
        if len(desc_str) > 24:
            desc_str = desc_str[:22] + "..."
            
        draw.text((180, current_y), desc_str, fill=(80, 80, 80), font=font_sub)
        
        current_y += 45 # 每一行行程往下跳 45 像素
        
    # 頂部跟底部畫個小尾巴
    draw.rectangle([0, 1170, 800, 1200], fill=(230, 247, 255))
    draw.text((40, 1175), "祝您旅途愉快！有任何問題歡迎隨時透過 LINE 聯絡我們", fill=(100, 100, 100), font=ImageFont.truetype("msjh.ttc", 14))

    # 6. 把圖片轉成二進位記憶體流，不存實體檔案，直接讓 Flask 送出下載
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return img_io
