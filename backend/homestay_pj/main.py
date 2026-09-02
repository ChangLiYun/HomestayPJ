from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file # 圖片輸出用

from app.models.booking import ( 
    add_booking, 
    get_all_bookings, 
    delete_booking)

from app.models.customer import (
    add_customer,
    get_all_customers,
    get_customer_by_id, 
    update_customer,
    delete_customer       
)
from app.models.room_type import (
    add_room_type, 
    get_all_room_types, 
    check_available_rooms)

from app.models.itinerary import (
    get_all_templates, 
    add_template, 
    add_template_detail,
    get_template_by_id, 
    get_template_details,
    delete_template_detail,
    delete_entire_template,
    apply_template_to_booking, 
    get_booking_itinerary,
    get_detail_by_id,
    update_template_detail,
    generate_itinerary_jpg)


app = Flask(
    __name__,
    template_folder="app/templates"
)

# 👉📋🔍 🧭
@app.route("/")
def home():
    return render_template("index.html")



@app.route("/customer/add", methods=["GET", "POST"])
@app.route("/customer/add", methods=["GET", "POST"])
def customer_add():
    if request.method == "POST":
        # 這裡只傳入姓名和電話給資料庫
        add_customer(
            request.form["customer_name"],
            request.form["phone"]
        )
        return redirect("/customer/list")

    return render_template("add_customer.html")



@app.route("/customer/list")
def customer_list():

    customers = get_all_customers()

    return render_template(
        "customer_list.html",
        customers=customers
    )

@app.route("/customer/edit/<int:customer_id>", methods=["GET", "POST"])
def customer_edit(customer_id):
    if request.method == "POST":
        # ⭕ 只傳送 2 個欄位（姓名、電話）和 ID 給更新功能
        update_customer(
            customer_id,
            request.form["customer_name"],
            request.form["phone"]
        )
        return redirect("/customer/list")
    
    customer = get_customer_by_id(customer_id)
    return render_template("edit_customer.html", customer=customer)



@app.route("/customer/delete/<int:customer_id>")
def customer_delete(customer_id):
    # 執行刪除
    delete_customer(customer_id)
    
    return redirect("/customer/list")

# 房型列表頁面
@app.route("/room_type/list")
def room_type_list():
    room_types = get_all_room_types()
    return render_template("room_type_list.html", room_types=room_types)

#----------------------------------------------------------------------------------
# 新增房型頁面
@app.route("/room_type/add", methods=["GET", "POST"])
def room_type_add():
    if request.method == "POST":
        add_room_type(
            request.form["room_name"],
            int(request.form["capacity"]),
            int(request.form["total_rooms"])
        )
        # 新增成功後，自動跳轉回房型列表！
        return redirect("/room_type/list")

    return render_template("add_room_type.html")

# 刪除房型
@app.route("/room_type/delete/<int:room_type_id>")
def room_type_delete(room_type_id):
    import sqlite3
    import os
    
    try:
        # 從 main.py 的位置精準定位到根目錄的資料庫
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../database/homestaypj.db"))
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM RoomType WHERE RoomTypeId = ?", (room_type_id,))
        conn.commit()
        conn.close()
        print(f"房型 ID {room_type_id} 刪除成功")
    except Exception as e:
        print(f"刪除失敗: {e}")
        
    return redirect("/room_type/list")

#----------------------------------------------------------------------------------
# 訂房紀錄列表
@app.route("/booking/list")
def booking_list():
    bookings = get_all_bookings()
    return render_template("booking_list.html", bookings=bookings)

# 填寫新訂房表單
@app.route("/booking/add", methods=["GET", "POST"])
def booking_add():
    if request.method == "POST":
        # 1. 接收前端傳過來的訂房條件
        target_room_type_id = int(request.form["room_type_id"])
        checkin_date = request.form["checkin"]
        checkout_date = request.form["checkout"]
        note = request.form.get('note', '')
        
        # 2. 悄悄先去查一下這段時間所有房型的剩餘空房
        from app.models.room_type import check_available_rooms
        available_rooms = check_available_rooms(checkin_date, checkout_date)
        
        # 3. 找出使用者選的那一種房型，看看它的剩餘空房剩幾間
        is_available = False
        for room in available_rooms:
            # room 是 RoomTypeId，room 是 剩餘空房數量
            if room[0] == target_room_type_id and room[5] > 0:
                is_available = True
                break
        
        # 4. 判斷是否能放行
        if is_available:
            # 還有空房，放行！寫入資料庫
            add_booking(
                int(request.form["customer_id"]),
                target_room_type_id,
                checkin_date,
                checkout_date,
                int(request.form["guest_count"]),
                note
            )
            return redirect("/booking/list")
        else:
            # 沒空房了！直接攔截並返回警告純文字，不允許寫入資料庫
            # 用 JavaScript 彈出視窗，並用 history.back() 讓使用者退回原頁面
            return """
            <script>
                alert("❌ 登記失敗：該時段此房型已無空房，請重新選擇日期或房型！");
                window.history.back(); // 自動退回上一頁，保留原本填寫的內容
            </script>
            """
       
    customers = get_all_customers()
    from app.models.room_type import get_all_room_types
    room_types = get_all_room_types()
    return render_template("add_booking.html", customers=customers, room_types=room_types)


# 空房查詢頁面
@app.route("/booking/search", methods=["GET", "POST"])
def booking_search():
    available_rooms = None
    start_date = None
    end_date = None

    if request.method == "POST":
        start_date = request.form["checkin"]
        end_date = request.form["checkout"]
        # 呼叫資料庫計算空房
        available_rooms = check_available_rooms(start_date, end_date)

    return render_template(
        "booking_search.html", 
        available_rooms=available_rooms, 
        start_date=start_date, 
        end_date=end_date
    )

# 刪除訂房紀錄
@app.route("/booking/delete/<int:booking_id>")
def booking_delete(booking_id):
    delete_booking(booking_id)
    # 刪除後自動跳轉回訂房總覽，畫面就會一秒刷新！
    return redirect("/booking/list")

# --- 行程模板 ----------------------------------------------------------------------
@app.route("/template/list")
def template_list():
    """查看行程模板總覽"""
    templates = get_all_templates()
    return render_template("template_list.html", templates=templates)

@app.route("/template/add", methods=["GET", "POST"])
def template_add():
    """新增行程模板與初始化明細"""
    if request.method == "POST":
        # 1. 接收網頁傳過來的所有欄位
        template_name = request.form["template_name"]
        day_number = int(request.form["day_number"])
        activity_time = request.form["activity_time"]
        description = request.form["description"]
        
        # 2. 呼叫 model 先建立模板主體，並拿到剛剛生成的 TemplateId
        t_id = add_template(template_name)
        
        # 3. 呼叫 model 把網頁填寫的真實行程細節塞入 TemplateDetail 資料表
        add_template_detail(t_id, day_number, activity_time, description)
        
        # 4. 大功告成，帶老闆娘跳轉回總覽列表
        return redirect("/template/list")
        
    return render_template("add_template.html")

@app.route("/template/detail/<template_id>/add", methods=["POST"])
def template_detail_add(template_id):
    day_number = int(request.form["day_number"])
    activity_time = request.form["activity_time"]
    
    # 💡 接收三個新格子
    act_name = request.form["act_name"]
    act_note = request.form.get("act_note", "")
    act_place = request.form.get("act_place", "")
    
    # 💡 魔術合體！用直線串起來存進資料庫
    full_description = f"{act_name}｜{act_note}｜{act_place}"
    
    add_template_detail(template_id, day_number, activity_time, full_description)
    return redirect(f"/template/detail/{template_id}")


@app.route("/template/detail/<int:template_id>")
def template_detail(template_id):
    # 1. 乖乖撈出該模板底下的所有行程明細列表即可
    details = get_template_details(template_id)
    
    # 2. 只需要傳這兩個變數給前端，保證不會再跳 NameError！
    return render_template(
        "template_detail.html", 
        details=details, 
        template_id=template_id
    )


@app.route("/template/detail/<template_id>/delete/<detail_id>")
def template_detail_delete(template_id, detail_id):
    """刪除模板中的某一筆行程時段"""
    # 執行刪除（記得去 itinerary.py 補上 delete_template_detail 函數喔！）
    delete_template_detail(int(detail_id))
    
    # 刪除成功後，自動帶老闆娘回到剛剛那個模板的細節頁面！
    return redirect(f"/template/detail/{template_id}")

@app.route("/template/delete/<int:template_id>")
def template_delete_main(template_id):
    """在總覽頁面刪除整套行程模板"""
    delete_entire_template(template_id)
    # 刪除完後，重新整理總覽列表
    return redirect("/template/list")

@app.route("/template/detail/<template_id>/edit/<detail_id>", methods=["GET", "POST"])
def template_detail_edit(template_id, detail_id):
    """編輯單一筆行程景點時段（升級三格拆分版）"""
    if request.method == "POST":
        day_number = int(request.form["day_number"])
        activity_time = request.form["activity_time"]
        
        # 💡 1. 接收編輯網頁傳回來的三個獨立欄位
        act_name = request.form["act_name"]
        act_note = request.form.get("act_note", "")
        act_place = request.form.get("act_place", "")
        
        # 💡 2. 重新拼接成一串，更新回資料庫
        full_description = f"{act_name}｜{act_note}｜{act_place}"
        
        update_template_detail(int(detail_id), day_number, activity_time, full_description)
        return redirect(f"/template/detail/{template_id}")
        
    # GET 模式：撈出舊資料
    detail_data = get_detail_by_id(int(detail_id))
    # detail_data[4] 是原本的 Description 景點描述
    raw_desc = detail_data[4] if detail_data else ""
    
    # 💡 3. 魔術拆分！把舊資料用 ｜ 切開，準備帶入網頁的三個格子裡
    parts = raw_desc.split("｜")
    name_val = parts[0] if len(parts) > 0 else raw_desc
    note_val = parts[1] if len(parts) > 1 else ""
    place_val = parts[2] if len(parts) > 2 else ""
    
    # 💡 4. 把切好的三個變數一起打包丟給 HTML
    return render_template(
        "template_detail_edit.html", 
        template_id=template_id, 
        detail=detail_data,
        name_val=name_val,
        note_val=note_val,
        place_val=place_val
    )

#------------------------------------------------------------------------------------
@app.route("/booking/apply_template/<int:booking_id>", methods=["POST"])
def booking_apply_template(booking_id):
    """接收前端送來的範本 ID，幫訂單套用行程"""
    template_id = int(request.form["template_id"])
    
    # 呼叫剛寫好的複製複製大法
    apply_template_to_booking(booking_id, template_id)
    
    # 套用成功後，直接跳轉到「這個客人的專屬行程查看頁面」！
    return redirect(f"/booking/itinerary/{booking_id}")


@app.route("/booking/itinerary/<int:booking_id>")
def booking_itinerary_view(booking_id):
    """觀看並客製化某個客戶訂單的專屬行程"""
    # 1. 為了畫面好看，我們順便撈一下這筆訂單的主資訊（如客人姓名、房型）
    from app.models.booking import get_all_bookings
    all_b = get_all_bookings()
    current_b = None
    for b in all_b:
        if b[0] == booking_id:
            current_b = b # 找到這筆訂單了！
            break
            
    # 2. 撈出這個客人的客製化行程清單
    itinerary_list = get_booking_itinerary(booking_id)
    
    # 3. 順便把所有可用的「行程模板」撈出來，以備老闆娘隨時想改套別的範本
    templates = get_all_templates()
    
    return render_template("booking_itinerary.html", booking=current_b, itinerary=itinerary_list, templates=templates)

#--- 圖片輸出 -------------------------------------------------------------------------------

@app.route("/booking/export_jpg/<int:booking_id>")
def booking_export_jpg(booking_id):
    """一鍵產出客人的專屬行程 JPG 卡片提供下載"""
    # 1. 撈出這筆訂單的主資訊
    from app.models.booking import get_all_bookings
    all_b = get_all_bookings()
    current_b = None
    for b in all_b:
        if b[0] == booking_id: # 💡 確保比對的是第一個元素 BookingId
            current_b = b
            break
            
    if not current_b:
        return "❌ 找不到該筆訂單", 404
        
    # 2. 撈出這個客人目前已經套用的客製化行程清單
    from app.models.itinerary import get_booking_itinerary
    itinerary_list = get_booking_itinerary(booking_id)
    
    # 3. 丟給 Pillow 工廠開始畫圖，拿到記憶體圖片檔案
    from app.models.itinerary import generate_itinerary_jpg
    img_stream = generate_itinerary_jpg(current_b, itinerary_list)
    
    # 4. 💡 修正亮點：根據你早上寫的 SQL 順序，c.CustomerName 是在第二個位置（索引值 1）
    customer_name = current_b[1] 
    
    # 防呆：萬一名字讀出來真的是 None，給個預設檔名防止系統大崩潰
    if not customer_name:
        customer_name = f"Guest_{booking_id}"
        
    filename = f"Itinerary_{customer_name}.jpg"
    
    img_stream.name = filename
    
    # 送出下載
    return send_file(
        img_stream, 
        mimetype='image/jpeg', 
        as_attachment=True, 
        download_name=filename
    )



if __name__ == "__main__":
    app.run(debug=True)