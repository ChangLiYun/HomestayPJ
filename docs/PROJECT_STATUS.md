# HomestayPJ 專案狀態 

## 專案名稱

HomestayPJ - 民宿行程規劃與 ERP 財務管理系統

## 專案目標

先完成：

- 客戶管理 (CRUD) ✓ 已完成
- 房型管理 (CRUD) ✓ 已完成
- 訂房與空房管理 --- 進行中---
- 行程規劃與模板
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
│       │   │   └─ booking_search.html (空房前端報表編號已修正完畢)
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
│   ├─ schema.sql        (Customer, RoomType, Booking, Payment, BookingService)
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

### Database

- SQLite 建立完成
- homestaypj.db 建立完成

### Schema

已建立：

- Customer
- Itinerary
- Template
- TemplateDetail

###  客戶管理 (Customer)
-  新增客戶表單與資料寫入。
-  客戶列表動態讀取與展示。
-  編輯客戶功能 (帶入舊資料並執行 UPDATE)。
-  刪除客戶功能 (帶有 onclick 確認視窗並執行 DELETE)。
-  客戶 CRUD 徹底對齊「資料庫正規化」，完全剝離日期/人數等冗餘欄位。
-  修正 `edit_customer.html` 的前端索引值，徹底消滅 tuple 組合包括號。

###  房型管理 (RoomType)
-  房型列表頁面建立，成功讀取房型資料。
-  新增房型與房型列表動態讀取。

###  訂房管理 (Booking)
-  實作 SQL `JOIN` 跨表調閱，訂房列表完美顯示姓名與房型。
-  修正 `booking_search.html` 的前端呈現，完美動態顯示「房型、總間數、已訂數、剩餘空房」。
-  **防超賣安全機制 (Overbooking Shield)**：在 `/booking/add` 後端加入驗證，
    若剩餘空房 `<= 0` 則直接由 JavaScript 彈窗攔截失敗，並自動退回上一頁，絕不寫入資料庫。
-  **刪除訂房 (Delete Booking)**：補齊訂房列表的刪除功能，利於排房資料清理與測試防護網。


---

## 下一步

### 1. 驗證空房即時查詢
- [ ] 輸入日期區間，驗證「日期衝突排除演算法」是否能精準算出「總房間數 - 已訂房間 = 剩餘空房」。

### 2. 推進至行程規劃與輸出 
- [ ] 行程管理 (Itinerary) CRUD 開發。
- [ ] 行程模板套用功能。
- [ ] 研議 Pillow 庫進行 JPG 行程卡匯出。

### 未來功能

#### 行程規劃

- Itinerary CRUD
- 行程模板套用

#### JPG 匯出

- Pillow 產圖
- 行程卡匯出

#### ERP

- Payment
- BookingService

#### 空房查詢

輸入：

入住日期
退房日期

輸出：

雙人房剩餘數量
四人房剩餘數量

---

## 已知問題

- .gitignore Merge Conflict 尚待整理

