from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
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
    get_booking_itinerary)


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

@app.route("/template/detail/<int:template_id>/add", methods=["POST"])
def template_detail_add(template_id):
    """在細節頁面中直接幫該模板追加新的景點時段"""
    day_number = int(request.form["day_number"])
    activity_time = request.form["activity_time"]
    description = request.form["description"]
    
    # 呼叫我們之前就寫好的 add_template_detail 函數
    add_template_detail(template_id, day_number, activity_time, description)
    
    # 💡 亮點：新增完後，直接自動跳轉回「原本這個模板的細節頁面」，畫面一重新整理就能看到新行程！
    return redirect(f"/template/detail/{template_id}")

@app.route("/template/detail/<template_id>")
def template_detail(template_id):
    """查看行程模板的每日詳細景點"""
    # 確保轉成整數去查資料庫
    t_id = int(template_id)
    
    # 1. 撈出模板主資訊
    template = get_template_by_id(t_id)
    
    # 2. 撈出該模板底下的所有行程明細
    details = get_template_details(t_id)
    
    # 3. 丟給前端網頁渲染
    return render_template("template_detail.html", template=template, details=details)

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



if __name__ == "__main__":
    app.run(debug=True)
