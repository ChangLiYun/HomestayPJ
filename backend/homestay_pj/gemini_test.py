import os
import sqlite3
from google import genai

# =====================================================================
# 步驟 1：請先在終端機（Terminal）安裝最新的 Google 官方套件
# 指令：pip install google-genai
# =====================================================================

# 1. 初始化 Gemini 用戶端（請把後面的引號換成你從 Google AI Studio 申請到的金鑰）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. 這是我們要餵給 Gemini 看的「犯嫌程式碼」（也就是你目前卡住的大法與 HTML）
# 這裡我幫你把這兩段 code 當作背景資料包起來
code_context = """
【後端複製大法（itinerary.py）】
def apply_template_to_booking(booking_id, template_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Itinerary WHERE BookingId = ?", (booking_id,))
    cursor.execute("SELECT DayNumber, ActivityTime, Description FROM TemplateDetail WHERE TemplateId = ?", (template_id,))
    details = cursor.fetchall()
    for d in details:
        cursor.execute("INSERT INTO Itinerary (BookingId, DayNumber, ActivityTime, Description) VALUES (?, ?, ?, ?)", (booking_id, d[0], d[1], d[2]))
    conn.commit()
    conn.close()

【前端 HTML 表格（booking_itinerary.html）】
{% if itinerary %}
    {% for d in itinerary %} 
        {% set parts = d[4].split('｜') %}
        ...
        <td>第 {{ d[2] }} 天</td>
        <td>{{ d[3] }}</td>
    {% endfor %}
{% else %}
    💡 目前這位客人還沒有任何行程。
{% endif %}
"""

# 3. 設定你想要問 Gemini 的問題
user_question = "我按了執行套用，但畫面一直掉進 else 顯示『目前這位客人還沒有任何行程』，請幫我找出真正的原因並給我修正代碼！"

# 4. 把程式碼和問題組合起來，並設定角色給 Gemini
prompt = f"""
你是一位精通 Python Flask 與 SQLite 的資深後端工程師。
以下是我的專案程式碼片段：
{code_context}

我的問題：{user_question}
"""

print("⏳ 正在連線至 Gemini 2.5 Flash 進行硬核除錯...")

# 5. 正式呼叫最新模型
response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt,
)

# 6. 把 Gemini 幫你抓出來的 Bug 答案印在終端機上
print("\n=== 🎯 Gemini 幫你找到的 Bug 診斷報告 ===")
print(response.text)
