from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from app.models.booking import ( 
    add_booking, 
    get_all_bookings)

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
    # 如果使用者點擊送出修改（POST）
    if request.method == "POST":
        update_customer(
            customer_id,
            request.form["customer_name"],
            request.form["phone"],
            request.form["checkin"],
            request.form["checkout"],
            request.form["guest_count"]
        )
        # 修改成功後，直接跳轉回客戶列表頁面
        from flask import redirect, url_for
        return redirect("/customer/list")

    # 如果使用者只是剛點進來（GET），先抓取舊資料顯示在網頁表單上
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
        add_booking(
            int(request.form["customer_id"]),
            int(request.form["room_type_id"]),
            request.form["checkin"],
            request.form["checkout"],
            int(request.form["guest_count"])
        )
        return redirect("/booking/list")

    # GET 請求時，要把所有「客戶」和「房型」撈出來，讓前端做成下拉選單（選單裡才會有孫老師、張主任、雙人房可以選）
    customers = get_all_customers()
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



if __name__ == "__main__":
    app.run(debug=True)
