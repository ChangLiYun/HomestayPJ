# HomestayPJ 專案狀態 

## 專案名稱

HomestayPJ - 民宿行程規劃與 ERP 財務管理系統

## 專案目標

先完成：
- 客戶管理 (CRUD) ✓ 已完成
- 房型管理 (CRUD) ✓ 已完成
- 訂房與空房管理 ✓ 基礎功能進行中
- 行程規劃與模板 ⏳ 排序優化與正規化進行中
- JPG 匯出

後續擴充：
- 訂房管理
- 房型管理
- 空房查詢
- ERP 財務管理
- 額外服務管理 (BookingService)

---

## 技術棧

Backend:
- Python
- Flask

Database:
- SQLite  (已成功實作多表關聯 JOIN)

Tools:
- VSCode
- SQLite Viewer
- Git
- GitHub

Future:
- MSSQL
- Power BI

---

## 目前目錄結構

```text
HomestayERP
│
├─ backend
│   └─ homestay_pj
│       ├─ app
│       │   ├─ models
│       │   │   ├─ customer.py   (已完成 CRUD)
│       │   │   ├─ room_type.py  (已完成 Add, List, 剩餘空房計算 SQL)
│       │   │   └─ booking.py    (已完成 Add,  List JOIN 查詢, Delete 功能)
│       │   ├─ templates
│       │   │   ├─ add_customer.html
│       │   │   ├─ edit_customer.html
│       │   │   ├─ customer_list.html
│       │   │   ├─ add_room_type.html
│       │   │   ├─ room_type_list.html
│       │   │   ├─ add_booking.html
│       │   │   ├─ booking_list.html
│       │   │   ├─ booking_search.html    (空房前端報表編號已修正完畢)
│       │   │   ├─ booking_itinerary.html (行程模板明細管理)
│       │   │   └─ template_list.html     (行程模板列表)
│       │   ├─ routes
│       │   ├─ services
│       │   └─ static
│       │
│       ├─ main.py       (防超賣驗證、彈窗攔截與自動跳轉路由已補齊)
│       ├─ config.py
│       ├─ init_db.py    (資料庫施工工人，已成功跑完 schema.sql)
│       └─ requirements.txt
│
├─ database
│   ├─ homestaypj.db   
│   ├─ schema.sql        (Customer, RoomType, Booking, Payment, BookingService, Itinerary, Template, TemplateDetail)
│   └─ sample_data.sql
```

---

## 已完成

### Python 環境
- venv 建立完成
- requirements 安裝完成

### Git
- git init 完成
- GitHub Repository 建立完成

### Flask
- main.py 建立完成
- localhost:5000 啟動成功

### Database & Schema
- SQLite 建立完成
- homestaypj.db 建立完成
- 已建立 Table 結構：Customer, Itinerary, Template, TemplateDetail

## 專案目標達成狀況

###  客戶管理 (Customer)
- 新增客戶表單與資料寫入。
- 客戶列表動態讀取與展示。
- 編輯客戶功能 (帶入舊資料並執行 UPDATE)。
- 刪除客戶功能 (帶有 onclick 確認視窗並執行 DELETE)。
- 客戶 CRUD 徹底對齊「資料庫正規化」，完全剝離日期/人數等冗餘欄位。
- 修正 `edit_customer.html` 的前端索引值，徹底消滅 tuple 組合包括號。
#### --- 260828 -----
- 客戶 CRUD 功能完全對齊「資料庫正規化」，完全剝離 redundant 冗餘欄位。
- 前端介面排版優化：完成 `customer_list.html` 寬度配比，表格內襯調整為舒適的 `padding: 8px`，徹底消滅貼邊擁擠感。


###  房型管理 (RoomType)
- 房型列表頁面建立，成功讀取房型資料。
- 新增房型與房型列表動態讀取。
#### --- 260828 -----
- 房型新增與列表功能。
- 前端介面排版優化：完成 `room_type_list.html` 精緻微調（`max-width: 500px`），視覺空間感拉滿。


###  訂房管理 (Booking)
- 實作 SQL `JOIN` 跨表調閱，訂房列表完美顯示姓名與房型。
- 修正 `booking_search.html` 的前端呈現，完美動態顯示「房型、總間數、已訂數、剩餘空房」。
- **防超賣安全機制 (Overbooking Shield)**：在 `/booking/add` 後端加入驗證，若剩餘空房 `<= 0` 則直接由 JavaScript 彈窗攔截失敗，並自動退回上一頁，絕不寫入資料庫。
- 刪除訂房 (Delete Booking)：補齊訂房列表的刪除功能，利於排房資料清理與測試防護網。
#### --- 260828 -----
- **防超賣安全機制 (Overbooking Shield)**：成功實作後端自動衝突驗證，無空房時透過 JavaScript 彈窗攔截，絕不允許極端狀況寫入資料庫。
- **訂房備註欄位補齊 (Major Update)**：
    - 資料庫成功下達 `ALTER TABLE Booking ADD COLUMN Note TEXT;` 擴充。
    - 前端補齊 `add_booking.html` 的 `<textarea>` 備註大格子。
    - 修正 `booking_list.html` 在沒備註時自動隱形 `None` 字串的 Jinja2 判斷防呆。
- 輸入日期區間，前端報表完美自動核算「總房間數 - 已訂房間 = 剩餘空房」。

###  行程規劃與模板 (今日新增進度)
- **問題診斷與核心優化規劃**：診斷出行程明細在無 SQL 排序下會發生時間錯亂（如 12:50 跑到 9:50 上方）的 Bug。
#### --- 260828 -----
* **首頁架構正義**：將原 多行 HTML 字串，完美搬遷歸位至 `templates/index.html`，實現標準 MVC 架構。
* **資料庫地基落成**：順利在 SQLite 注入 3 張核心關聯表：`Template`、`TemplateDetail`、`Itinerary`。
* **行程模板 CRUD & 級聯刪除**：實作行程模板總覽與追加明細功能。具備「級聯清理 (Cascade Delete)」機制，刪除整套模板時，會連同底下的天數行程一網打盡，防止資料庫留下孤兒邊界數據。
* **時間軸正規化與自動排序 **：
  * 將前端文字輸入框強制前導零格式（如 `09:50`）。
  * 達成「修改時間，網頁重整自動插隊歸位」的防呆操作。
* **訂單套用模板核心主線**：在訂房紀錄總覽增設快捷入口，點擊即可進入專屬面板。實作一鍵複製大法，把公共範本細節完美改綁至客人的 `BookingId` 並存入 `Itinerary` 活資料表。
*
---

## 下一步

### 1. **研議將產圖引擎升級為「PDF 匯出引擎」**
   * 為了解決超長行程導致 JPG 被手機壓縮、畫質變差的天然物理漏洞，下階段預計導入 PDF 匯出技術，實現 A4 自動精準分頁、向量文字無限放大不破圖的頂級體驗。
### 2. **防超賣即時查詢前端對齊**
   * 完成日期重疊排除演算法的前端即時渲染。
### 3. **推進至 ERP 財務管理與額外服務**
   * 逐步開工 `Payment` 資料表，將「已付訂金、尾款、付款日期」與今天的預算表格做連動。

---

## 未來功能與擴充

### 行程規劃與 JPG 輸出
- Itinerary CRUD / 模板套用
- Pillow 產圖與行程卡匯出

### ERP 財務與空房
- Payment / BookingService 實作
- 精準空房查詢（輸入：入住/退房日期 -> 輸出：各房型剩餘數量）

---

## 已知問題
- .gitignore Merge Conflict 尚待整理
