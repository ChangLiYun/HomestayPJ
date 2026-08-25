# HomestayPJ 專案狀態 (2026-08-26 更新)

## 專案名稱

HomestayPJ - 民宿行程規劃與 ERP 財務管理系統

## 專案目標

先完成：

- 客戶管理 (CRUD) ✨ 已完成
- 房型管理 (CRUD) ✨ 已完成
- 訂房與空房管理 ✨ 進行中
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
│       │   │   ├─ room_type.py  (已完成 Add, List, 補上 Check 空房 SQL)
│       │   │   └─ booking.py    (已完成 Add, List JOIN 查詢)
│       │   ├─ templates
│       │   │   ├─ add_customer.html
│       │   │   ├─ edit_customer.html
│       │   │   ├─ customer_list.html
│       │   │   ├─ add_room_type.html
│       │   │   ├─ room_type_list.html
│       │   │   ├─ add_booking.html
│       │   │   ├─ booking_list.html
│       │   │   └─ booking_search.html (待前端測試驗證)
│       │   ├─ routes
│       │   ├─ services
│       │   └─ static
│       │
│       ├─ main.py       (首頁選單與所有核心路由已補齊，支援自動跳轉)
│       ├─ config.py
│       ├─ init_db.py    (資料庫施工工人，已成功跑完 schema.sql)
│       └─ requirements.txt
│
├─ database
│   ├─ homestaypj.db     (已全新重構，結構健康)
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
-  成功將入住日期/人數等訂單欄位剝離，回歸標準客戶基本資料。

###  房型管理 (RoomType)
-  新增房型 (房型名稱、可住人數、總房間數)。
-  解決 `no such table: RoomType` 錯誤，成功透過 `init_db.py` 重建全新乾淨資料庫。
-  房型列表頁面建立，成功讀取房型資料。

###  訂房管理 (Booking)
-  新增訂房訂單，前端採用下拉選單動態載入 Customer 與 RoomType。
-  實作 SQL `JOIN` 跨表調閱，成功在不重複儲存資料的原則下，於前端同時顯示客戶姓名、電話、房型名稱、入住日期與人數。
-  實作全面性的 `redirect` 跳轉機制，解決手動重新整理與一直按上一頁的痛點。

---

## 下一步

### 1. 驗證空房即時查詢
- [ ] 測試 `/booking/search` 路由。
- [ ] 輸入日期區間，驗證「日期衝突排除演算法」是否能精準算出「總房間數 - 已訂房間 = ✨ 剩餘空房」。

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

