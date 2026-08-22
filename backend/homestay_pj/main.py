from flask import Flask
from flask import render_template
from flask import request

from app.models.customer import add_customer

app = Flask(
    __name__,
    template_folder="app/templates"
)



@app.route("/")
def home():
    return """
    <h1>HomestayPJ</h1>
    <p>民宿行程規劃系統</p>
    
    <!-- 這裡就是修正後的正確超連結 -->
    <a href="/customer/add">👉 點我前往：新增客戶</a>
    """



@app.route("/customer/add", methods=["GET", "POST"])
def customer_add():

    if request.method == "POST":

        add_customer(
            request.form["customer_name"],
            request.form["phone"],
            request.form["checkin"],
            request.form["checkout"],
            request.form["guest_count"]
        )

        return "新增成功"

    return render_template("add_customer.html")


if __name__ == "__main__":
    app.run(debug=True)