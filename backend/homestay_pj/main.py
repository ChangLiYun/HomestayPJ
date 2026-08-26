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


app = Flask(
    __name__,
    template_folder="app/templates"
)


@app.route("/")
def home():
    return """
    <h1>HomestayPJ</h1>
    <p>民宿行程規劃系統</p>

    <h3>👥 客戶管理</h3>
    <a href="/customer/add">👉 新增客戶</a> | 
    <a href="/customer/list">📋 客戶列表</a>

    <h3>🛏️ 房型管理</h3>
    <a href="/room_type/add">👉 新增房型</a> | 
    <a href="/room_type/list">📋 房型列表</a>

    <h3>📅 訂房管理</h3>
    <a href="/booking/add">👉 登記新訂房</a> | 
    <a href="/booking/list">📋 訂房紀錄總覽</a> | 
    <a href="/booking/search">🔍 即時空房查詢</a>
    """



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
                int(request.form["guest_count"])
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



if __name__ == "__main__":
    app.run(debug=True)
