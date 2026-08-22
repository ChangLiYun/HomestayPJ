import sqlite3

DB_PATH = r"D:\HomestayERP\database\homestaypj.db"

def add_customer(
    customer_name,
    phone,
    checkin,
    checkout,
    guest_count
):
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Customer
        (
            CustomerName,
            Phone,
            CheckInDate,
            CheckOutDate,
            GuestCount
        )
        VALUES
        (?, ?, ?, ?, ?)
    """, (
        customer_name,
        phone,
        checkin,
        checkout,
        guest_count
    ))

    conn.commit()
    conn.close()