--建立資料表
/*
Customer
RoomType
Booking
Payment
BookingService
*/

-- 客戶資料

CREATE TABLE IF NOT EXISTS Customer (
    CustomerId INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerName TEXT NOT NULL,
    Phone TEXT,
    LineId TEXT,
    Note TEXT
);

CREATE TABLE IF NOT EXISTS RoomType (
    RoomTypeId INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT NOT NULL,
    Capacity INTEGER,
    TotalRooms INTEGER
);

CREATE TABLE IF NOT EXISTS Booking (
    BookingId INTEGER PRIMARY KEY AUTOINCREMENT,

    CustomerId INTEGER,
    RoomTypeId INTEGER,

    CheckInDate DATE,
    CheckOutDate DATE,

    GuestCount INTEGER,

    TotalAmount REAL,

    Status TEXT,

    FOREIGN KEY(CustomerId)
        REFERENCES Customer(CustomerId),

    FOREIGN KEY(RoomTypeId)
        REFERENCES RoomType(RoomTypeId)
);

CREATE TABLE IF NOT EXISTS Payment (
    PaymentId INTEGER PRIMARY KEY AUTOINCREMENT,

    BookingId INTEGER,

    DepositAmount REAL,

    PaidAmount REAL,

    PaymentDate DATE,

    FOREIGN KEY(BookingId)
        REFERENCES Booking(BookingId)
);

CREATE TABLE IF NOT EXISTS BookingService (
    BookingServiceId INTEGER PRIMARY KEY AUTOINCREMENT,

    BookingId INTEGER,

    ServiceName TEXT,

    Price REAL,

    FOREIGN KEY(BookingId)
        REFERENCES Booking(BookingId)
);

-- ========================================================
-- 後續擴充：行程規劃與模板系統
-- ========================================================

-- 1. 行程模板總表（例如：三天兩夜網美打卡行、兩天一夜親子慢活）
CREATE TABLE IF NOT EXISTS Template (
    TemplateId INTEGER PRIMARY KEY AUTOINCREMENT,
    TemplateName TEXT NOT NULL
);

-- 2. 行程模板每日細節（存死資料，用來給新訂單複製用）
CREATE TABLE IF NOT EXISTS TemplateDetail (
    DetailId INTEGER PRIMARY KEY AUTOINCREMENT,
    TemplateId INTEGER,
    DayNumber INTEGER,         -- 第幾天 (例如: 1, 2, 3)
    ActivityTime TEXT,         -- 時間描述 (例如: '10:00' 或 '下午')
    Description TEXT NOT NULL,  -- 行程景點內容 (例如: '高美濕地看夕陽')
    FOREIGN KEY(TemplateId) REFERENCES Template(TemplateId)
);

-- 3. 客戶客製化行程表（真正綁定訂單、要畫成 JPG 的活資料）
CREATE TABLE IF NOT EXISTS Itinerary (
    ItineraryId INTEGER PRIMARY KEY AUTOINCREMENT,
    BookingId INTEGER,         -- 💡 核心：這筆行程是屬於哪一張訂單的！
    DayNumber INTEGER,         -- 第幾天
    ActivityTime TEXT,         -- 時間描述
    Description TEXT NOT NULL,  -- 行程景點內容 (民宿老闆可以幫這個客人單獨修改)
    FOREIGN KEY(BookingId) REFERENCES Booking(BookingId)
);
