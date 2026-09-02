import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime, timedelta


# 穩固路徑法：直接切開路徑，找到 HomestayERP 根目錄的絕對位置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = CURRENT_DIR.split("backend")[0] # 自動切到 backend 之前的那一層（也就是 HomestayERP）
DB_PATH = os.path.join(BASE_DIR, "database", "homestaypj.db")
# 雲端環境專用判斷：如果偵測到是 Linux 雲端環境（沒有 D 槽），強迫將資料庫指向可寫入的 /tmp 專區
if not os.path.exists("D:\\"):
    DB_PATH = "/tmp/homestaypj.db"
# ========================================================
# 1. 行程模板管理 (基礎 CRUD 函數)
# ========================================================

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
    template_id = cursor.lastrowid
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
    cursor.execute("DELETE FROM TemplateDetail WHERE TemplateId = ?", (template_id,))
    cursor.execute("DELETE FROM Template WHERE TemplateId = ?", (template_id,))
    conn.commit()
    conn.close()

# ========================================================
# 2. 客戶訂單行程套用與查詢 (主線任務函數)
# ========================================================

def apply_template_to_booking(booking_id, template_id):
    """將指定的行程模板複製一份，正式綁定到該筆訂房訂單上"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Itinerary WHERE BookingId = ?", (booking_id,))
    
    cursor.execute("SELECT DayNumber, ActivityTime, Description FROM TemplateDetail WHERE TemplateId = ?", (template_id,))
    details = cursor.fetchall()
    
    # 🚨 補上這行測試 1
    print(f" LOG: 點擊套用！從範本庫 (ID: {template_id}) 抓到 {len(details)} 筆行程。")
    
    for d in details:
        cursor.execute("""
            INSERT INTO Itinerary (BookingId, DayNumber, ActivityTime, Description)
            VALUES (?, ?, ?, ?)
        """, (booking_id, d[0], d[1], d[2]))
        
    conn.commit()
    conn.close()
    print(" LOG: 資料庫已 commit 存盤並關閉連線。")


def get_booking_itinerary(booking_id):
    """撈出某筆訂房訂單目前已經綁定的專屬客製化行程（精準對齊前端 d[2], d[3], d[4] 索引值）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 💡 亮點：我們把 BookingId 補進 SELECT 的第二個位置，這樣後面 2, 3, 4 的順序就完全對齊了！
    cursor.execute("""
        SELECT ItineraryId, BookingId, DayNumber, ActivityTime, Description 
        FROM Itinerary 
        WHERE BookingId = ?
        ORDER BY DayNumber ASC, ActivityTime ASC
    """, (booking_id,))
    itinerary_list = cursor.fetchall()
    conn.close()
    return itinerary_list

# d[0] ＝ ItineraryId
# d[1] ＝ BookingId
# d[2] ＝ DayNumber (天數，對應前端的 第 {{ d[2] }} 天)
# d[3] ＝ ActivityTime (時間，對應前端的 {{ d[3] }})
# d[4] ＝ Description (這就是帶有 ｜ 的魔術字串)

# ========================================================
# 3. Notion 表格自動繪製與換行引擎 (海顏還原版)
# ========================================================

def draw_text_wrapped(draw, text, x, y, font, fill, max_width, line_height=26):
    """強大換行幫手：在指定格子寬度內自動換行，並回傳總共佔用了多少高度"""
    if not text:
        return y
    words = list(text)
    current_line = ""
    start_y = y
    
    for word in words:
        test_line = current_line + word
        left, top, right, bottom = draw.textbbox((0, 0), test_line, font=font)
        text_width = right - left
        
        if text_width <= max_width:
            current_line = test_line
        else:
            draw.text((x, y), current_line, fill=fill, font=font)
            y += line_height
            current_line = word
            
    if current_line:
        draw.text((x, y), current_line, fill=fill, font=font)
        y += line_height
        
    return y - start_y

def generate_itinerary_jpg(booking_info, itinerary_list):
    """【海顏 Notion 風】終極還原產圖引擎 (安全對齊版)"""
    img = Image.new("RGB", (900, 2500), color=(255, 255, 255)) # 稍微再拉長畫布防擠壓
    draw = ImageDraw.Draw(img)

    current_y = 0  # 💡 先在這初始化 current_y

    # 絕對路徑
    BANNER_PATH = r"D:\HomestayERP\banner.jpg"


    if os.path.exists(BANNER_PATH):
        # 2. 打開你的 banner 圖
        banner = Image.open(BANNER_PATH)
        
        # 💡 假設你的大畫布寬度是 1200 像素，我們可以把 banner 縮放到跟畫布一樣寬
        # 這裡的 canvas_width 請對照你原本寫的白色底圖寬度
        canvas_width = 900 
        banner_w, banner_h = banner.size
        scale = canvas_width / banner_w
        banner_resized = banner.resize((canvas_width, int(banner_h * scale)))
        
        # 3. 貼上大畫布的最頂端 (0, 0) 位置
        # 註：如果貼了 banner，下面的標題與表格的 Y 軸起始點（current_y）記得要加上 banner_resized.height 往下推！
        img.paste(banner_resized, (0, 0))
        current_y += banner_resized.height + 20 

    try:
        font_main_title = ImageFont.truetype("msjh.ttc", 36)
        font_day_title = ImageFont.truetype("msjh.ttc", 22)
        font_th = ImageFont.truetype("msjh.ttc", 16)
        font_td = ImageFont.truetype("msjh.ttc", 15)
        font_td_bold = ImageFont.truetype("msjh.ttc", 15)
    except IOError:
        font_main_title = font_day_title = font_th = font_td = font_td_bold = ImageFont.load_default()

    # # 頂部照片區塊（原 40~300 高度差為 260，我們改用 current_y 來往下疊加）
    block_top = current_y + 10
    block_bottom = current_y + 270

    # draw.rectangle([(50, block_top), (850, block_bottom)], fill=(240, 245, 250), outline=(220, 225, 230), width=1)
    # draw.text((360, block_top + 110), "【 海顏民宿 HAIYEN 】", fill=(100, 110, 120), font=font_day_title)
    current_y += 30
    # 4. 標題（旅遊規劃）
    draw.text((50, current_y + 30), "旅遊規劃", fill=(0, 0, 0), font=font_main_title)
    current_y += 100 # 畫完標題，將 Y 軸往下推 100 像素給客人資訊
    
    # 💡 關鍵對齊點：根據 get_all_bookings 的 Tuple 索引值精準拆解
    c_name = booking_info[1]      # 客人姓名 (CustomerName)
    r_name = booking_info[2]      # 房型名稱 (RoomName)
    checkin_str = booking_info[3]  # 入住日期 (CheckInDate)
    checkout_str = booking_info[4] # 退房日期 (CheckOutDate)
    
    info_text = f"入住期間：{checkin_str} ～ {checkout_str}"
    draw.text((50, current_y), info_text, fill=(100, 100, 100), font=font_day_title, spacing=10)

    # 💡 計算 info_text 總共佔了三行字的高度，大約 110 像素
    current_y += 110    
    
    # # 6. 設定表格各個欄位的 X 軸起跑點與寬度
    col_x = {'time': 50, 'name': 150, 'note': 400, 'place': 700}
    col_w = {'time': 80, 'name': 220, 'note': 270, 'place': 130}

    # 按天分組
    itinerary_by_day = {}
    for item in itinerary_list:
        day_num = item[2] # 行程明細的 DayNumber 在第三個位置 (索引值 2)
        if day_num not in itinerary_by_day:
            itinerary_by_day[day_num] = []
        itinerary_by_day[day_num].append(item)
        
    current_y += 20
    draw.text((50, current_y), "每日行程", fill=(50, 50, 50), font=font_day_title)
    current_y += 40
    
    for day_num in sorted(itinerary_by_day.keys()):
        # 💡 安全防呆日期計算：萬一格式不對直接抓字串，絕對不當機
        try:
            start_date = datetime.strptime(str(checkin_str), "%Y-%m-%d")
            current_date = start_date + timedelta(days=int(day_num) - 1)
            date_display = current_date.strftime("%m-%d")
        except Exception:
            date_display = f"第 {day_num} 天"
            
        draw.rectangle([(50, current_y), (55, current_y+25)], fill=(0, 102, 204))
        draw.text((65, current_y), f"{date_display}  第 {day_num} 天", fill=(0, 0, 0), font=font_day_title)
        current_y += 45
        
        # 表格標頭
        draw.rectangle([(50, current_y), (850, current_y+35)], fill=(250, 250, 250), outline=(230, 230, 230), width=1)
        draw.text((col_x['time']+10, current_y+8), " 時間", fill=(120, 120, 120), font=font_th)
        draw.text((col_x['name']+10, current_y+8), " 活動名稱", fill=(120, 120, 120), font=font_th)
        draw.text((col_x['note']+10, current_y+8), " 備註", fill=(120, 120, 120), font=font_th)
        draw.text((col_x['place']+10, current_y+8), " 地點", fill=(120, 120, 120), font=font_th)
        current_y += 35
        
        for item in itinerary_by_day[day_num]:
            time_val = item[3] # 行程明細的 ActivityTime 在第三個位置
            desc_val = item[4] # 行程明細的 Description 在第四個位置
            
            parts = desc_val.split("｜")
            name_text = parts[0] if len(parts) > 0 else desc_val
            note_text = parts[1] if len(parts) > 1 else ""
            place_text = parts[2] if len(parts) > 2 else ""
            
            h_name = draw_text_wrapped(ImageDraw.Draw(Image.new("RGB", (1,1))), name_text, 0, 0, font_td, (0,0,0), col_w['name'])
            h_note = draw_text_wrapped(ImageDraw.Draw(Image.new("RGB", (1,1))), note_text, 0, 0, font_td, (0,0,0), col_w['note'])
            row_height = max(h_name, h_note, 40) + 20
            
            draw.rectangle([(50, current_y), (850, current_y+row_height)], outline=(230, 230, 230), width=1)
            draw.line([(col_x['name'], current_y), (col_x['name'], current_y+row_height)], fill=(230, 230, 230), width=1)
            draw.line([(col_x['note'], current_y), (col_x['note'], current_y+row_height)], fill=(230, 230, 230), width=1)
            draw.line([(col_x['place'], current_y), (col_x['place'], current_y+row_height)], fill=(230, 230, 230), width=1)
            
            draw.text((col_x['time']+15, current_y+12), str(time_val), fill=(80, 80, 80), font=font_td)
            
            draw_text_wrapped(draw, name_text, col_x['name']+15, current_y+12, font_td_bold, (0, 0, 0), col_w['name'])
            draw_text_wrapped(draw, note_text, col_x['note']+15, current_y+12, font_td, (100, 100, 100), col_w['note'])
            
            draw.text((col_x['place']+15, current_y+12), place_text, fill=(80, 80, 80), font=font_td)
            
            current_y += row_height
            
        current_y += 40
#---- 輸出的[預算花費]表 ----------------------------------------------------------------
        
    # current_y += 20 #留白
    # draw.text((50, current_y), "預算花費", fill=(50, 50, 50), font=font_day_title)
    # current_y += 40
    
    # draw.rectangle([(50, current_y), (850, current_y+35)], fill=(250, 250, 250), outline=(230, 230, 230), width=1)
    # draw.text((col_x['time']+10, current_y+8), "📅 日期", fill=(120, 120, 120), font=font_th)
    # draw.text((col_x['name']+10, current_y+8), "Aa 項目", fill=(120, 120, 120), font=font_th)
    # draw.text((col_x['note']+10, current_y+8), "☑ 已付款", fill=(120, 120, 120), font=font_th)
    # draw.text((col_x['place']+10, current_y+8), "# 金額", fill=(120, 120, 120), font=font_th)
    # current_y += 35
    
    # for _ in range(3):
    #     draw.rectangle([(50, current_y), (850, current_y+45)], outline=(230, 230, 230), width=1)
    #     # 直線
    #     draw.line([(col_x['name'], current_y), (col_x['name'], current_y+45)], fill=(230, 230, 230), width=1)
    #     draw.line([(col_x['note'], current_y), (col_x['note'], current_y+45)], fill=(230, 230, 230), width=1)
    #     draw.line([(col_x['place'], current_y), (col_x['place'], current_y+45)], fill=(230, 230, 230), width=1)
        
    #     current_y += 45
#------------------------------------------------------------------------------------------
        
    final_img = img.crop((0, 0, 900, current_y + 80))
    img_io = io.BytesIO()
    final_img.save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return img_io # 💡 確保不論如何都百分之百回傳
