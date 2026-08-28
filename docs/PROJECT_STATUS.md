# HomestayPJ 專案狀態 

## 專案名稱

HomestayPJ - 民宿行程規劃與 ERP 財務管理系統

## 專案目標

先完成：
- 客戶管理 (CRUD) ✓ 
- 房型管理 (CRUD) ✓ 
- 訂房與空房管理 ✓ 
- 行程規劃與模板 ✓  (後續會繼續優化&正規化)
- JPG 匯出 ✓ 

後續擴充：
- 行程卡轉型 PDF 向量分頁引擎
- ERP 財務管理 (Payment 數據連動)
- 額外服務管理 (BookingService)

---

## 技術棧

Backend:
- Python
- Flask
- Pillow (圖片生成)

Database:
- SQLite  (純標準關聯 SQL 查詢，無 ORM)

Tools:
- VSCode
- SQLite Viewer
- Git
- GitHub
- Gemini 3.6 Flash (AI 協作除錯)

---

## 目前目錄結構

```text
HomestayERP
│
├─ banner.jpg    (根目錄全新置入的 LINE 行程確認卡官方大橫幅)
│
├─ backend
│   └─ homestay_pj
│       ├─ app
│       │   ├─ models
│       │   │   ├─ customer.py   (已完成 CRUD)
│       │   │   ├─ room_type.py  (已完成 Add, List)
│       │   │   └─ booking.py    (已完成 Add, List JOIN 查詢, Delete)
│       │   ├─ templates
│       │   │   ├─ index.html    (首頁乾淨 MVC 架構)
│       │   │   ├─ add_customer.html
│       │   │   ├─ booking_list.html
│       │   │   ├─ booking_search.html    (空房前端動態報表)
│       │   │   ├─ booking_itinerary.html (客戶專屬行程預覽面板 - 高質感 5 欄位新網格)
│       │   │   └─ template_list.html     (行程模板列表與明細管理)
│       │   ├─ routes
│       │   ├─ services
│       │   └─ static
│       │
│       ├─ main.py       (前後端變數對齊、路由轉址核心控制中心)
│       ├─ config.py
│       ├─ init_db.py    (精準定位根目錄資料庫)
│       └─ requirements.txt
│
├─ database
│   ├─ homestaypj.db   
│   ├─ schema.sql        (Customer, RoomType, Booking, Payment, BookingService, Template, TemplateDetail, Itinerary)
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

### 1. 客戶管理 (Customer CRUD)
- **資料庫規格化**：徹底對齊正規化原則，移除冗餘的日期、人數等跨表欄位，落實單一職責。
- **維護流程閉環**：動態實作新增客戶、列表調閱、以及帶入舊資料的資料編輯（UPDATE）功能。
- **安全刪除機制**：於前端配置 `onclick` 確認視窗，防止管理員誤觸刪除資料（DELETE）。
- **前端索引值校正**：修正 `edit_customer.html` 樣板語法，消滅 Tuple 元組包裹括號的顯示異常。

### 2. 房型管理 (RoomType CRUD)
- **基礎資料維護**：實作房型新增表單，完成後端資料寫入與房型列表的動態讀取展示。
- **介面佈局微調**：最佳化 `room_type_list.html` 的外觀參數（配置 `max-width: 500px` 限制），大幅提升視覺空間的留白與專業感。

### 3. 訂房管理與防超賣機制 (Booking)
- **跨表關聯查詢**：實作 SQL `JOIN` 技術，於訂房列表中完美動態呈現客戶姓名與所屬房型。
- **即時空房報表**：優化 `booking_search.html`，動態計算並展示「總間數、已訂數、剩餘空房」。
- **防超賣安全機制 (Overbooking Shield)**：後端即時核算剩餘空房，若數量 `<= 0` 則透過前端 JavaScript 彈窗攔截，安全退回上一頁，拒絕執行資料庫寫入。
- **測試防護網補齊**：完成訂房紀錄的刪除功能，利於排房資料的清理與極端狀態測試。

### 4. 行程時間軸自動排序 (Itinerary)
- **前端資料正規化**：全面導入 HTML5 `<input type="time">` 強制 24 小時制（如 09:50）與前導零格式。
- **資料庫層級排序**：激活 SQLite `ORDER BY DayNumber ASC, ActivityTime ASC`。使用者修改行程時間後，網頁重新整理即自動無縫歸位。
- **前後端架構對齊**：修正 `itinerary` 單複數命名矛盾，將結構擴充為 5 欄位架構，補齊 Jinja2 閉合標籤避免渲染中斷。

### 5. 品牌視覺行程卡生成引擎 (Pillow)
- **多欄位解構技術**：資料庫維持單欄 `Description`，Pillow 引擎利用 `.split("｜")` 自動拆解 [活動名稱、備註事項、地點位置] 並獨立畫入網格。
- **動態相對座標優化**：消除寫死 Y 軸座標，導入 `current_y` 累加接力機制，徹底解決圖文物理重疊問題。
- **商用橫幅自動縮放**：動態讀取根目錄 `banner.jpg`，自動等比例縮放至 900 像素寬並貼於頂端，營造極簡 Notion 風格。
- **輕量化介面重構**：安全卸載複雜的預算統計表格，改為無壓力純文字備註呈現，大幅提升操作流暢度。

---

## 階段性開發任務 (Next Steps)

### 1. 行程模組轉型 PDF 向量分頁引擎
- **解決瓶頸**：克服超長 JPG 行程卡天數過多時遭 LINE 物理壓縮導致字體失真的限制。
- **技術調研**：評估導入 `ReportLab` 或 `WeasyPrint`，利用 PDF 天然的「A4 規格自動分頁」與向量字型特性，確保高清晰度輸出。

### 2. ERP 財務管理系統開發
- **激活 Payment 資料表**：建立完整的付款、定金、尾款與付款日期紀錄後台。
- **實現數據連動**：將後台財務數據與行程產出的預算表欄位進行即時動態連動。

### 3. 已知問題維護
- [ ] 整理並解決 `.gitignore` 的 Merge Conflict 衝突。
---

## 下一步階段性開發任務 (Next Steps)

### 1. 行程模組轉型 PDF 向量分頁引擎
- **解決瓶頸**：克服超長 JPG 行程卡天數過多時，遭通訊軟體（如 LINE）物理壓縮導致字體失真的限制。
- **技術調研**：評估導入 `ReportLab` 或 `WeasyPrint` 框架。
- **核心目標**：利用 PDF 規格具備的「A4 自動分頁」與向量字型特性，實現高解析度的分頁輸出。

### 2. 即時空房與日期衝突排除演算法驗證
- **核心邏輯**：完整測試與驗證「日期衝突排除演算法」，確保在特定日期區間內，能精準計算「總房間數 - 已訂房間 = 剩餘空房」。
- **前端對齊**：優化即時查詢介面，達成查詢結果與後端計算邏輯的精準連動。

### 3. ERP 財務管理系統開發
- **資料表活化**：建立 `Payment` 資料表，實作「已付定金、尾款、付款日期」等核心財務欄位維護。
- **數據連動**：將後台財務數據與未來擴充的收支報表進行動態連動。

---

## 未來功能與擴充規劃 (Future Roadmap)

### 1. 財務與加購模組 (ERP & Services)
- 實作 `BookingService` 資料表，支援民宿內加購行程或機車租賃等額外服務管理。
- 整合 `Payment` 報表，產出民宿單月營收與訂單財務流水帳。

### 2. 空房查詢模組 (Availability Analytics)
- 獨立開發全功能空房查詢面板。
- 輸入指定入住與退房日期，系統將自動輸出各房型（如雙人房、四人房）的剩餘可供預訂數量。

---

## 已知問題與維護 (Known Issues)
- [ ] 釐清並解決 `.gitignore` 檔案的 Git Merge Conflict 衝突。

