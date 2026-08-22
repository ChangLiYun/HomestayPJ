--建立資料表
/*
Customer
RoomType
Booking
Payment
BookingService
*/

-- 客戶資料

CREATE TABLE Customer (
    CustomerId INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerName TEXT NOT NULL,
    Phone TEXT,
    LineId TEXT,
    Note TEXT
);

CREATE TABLE RoomType (
    RoomTypeId INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT NOT NULL,
    Capacity INTEGER,
    TotalRooms INTEGER
);

CREATE TABLE Booking (
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

CREATE TABLE Payment (
    PaymentId INTEGER PRIMARY KEY AUTOINCREMENT,

    BookingId INTEGER,

    DepositAmount REAL,

    PaidAmount REAL,

    PaymentDate DATE,

    FOREIGN KEY(BookingId)
        REFERENCES Booking(BookingId)
);

CREATE TABLE BookingService (
    BookingServiceId INTEGER PRIMARY KEY AUTOINCREMENT,

    BookingId INTEGER,

    ServiceName TEXT,

    Price REAL,

    FOREIGN KEY(BookingId)
        REFERENCES Booking(BookingId)
);