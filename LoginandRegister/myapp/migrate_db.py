import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_DB = os.path.join(BASE_DIR, "event_rental.db")
NEW_DB = os.path.join(BASE_DIR, "customers.db")

def migrate():
    # 1. Kết nối DB
    old_conn = sqlite3.connect(OLD_DB)
    old_conn.row_factory = sqlite3.Row
    
    new_conn = sqlite3.connect(NEW_DB)
    
    try:
        # 2. Tạo bảng users ở customers.db
        new_conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username   TEXT PRIMARY KEY,
                password   TEXT    NOT NULL,
                email      TEXT    DEFAULT '',
                full_name  TEXT    DEFAULT '',
                phone      TEXT    DEFAULT '',
                role       TEXT    DEFAULT 'customer',
                is_active  INTEGER DEFAULT 1,
                created_at TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        
        # 3. Copy dữ liệu users
        users = old_conn.execute("SELECT * FROM users").fetchall()
        for user in users:
            new_conn.execute("""
                INSERT OR IGNORE INTO users 
                (username, password, email, full_name, phone, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user["username"], user["password"], user["email"], user["full_name"], user["phone"], user["role"], user["is_active"], user["created_at"]))
        new_conn.commit()
        print(f"Da copy {len(users)} users sang customers.db")

        # 4. Tạo lại các bảng ở event_rental.db mà KHÔNG CÓ FK tới users
        old_conn.execute("PRAGMA foreign_keys = OFF;")
        
        # --- cart_items ---
        old_conn.execute("ALTER TABLE cart_items RENAME TO cart_items_old")
        old_conn.execute("""
            CREATE TABLE cart_items (
                username   TEXT    NOT NULL,
                product_id INTEGER NOT NULL,
                quantity   INTEGER NOT NULL DEFAULT 1,
                days       INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (username, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        old_conn.execute("INSERT INTO cart_items SELECT * FROM cart_items_old")
        old_conn.execute("DROP TABLE cart_items_old")
        
        # --- orders ---
        old_conn.execute("ALTER TABLE orders RENAME TO orders_old")
        old_conn.execute("""
            CREATE TABLE orders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL,
                total      INTEGER NOT NULL DEFAULT 0,
                status     TEXT    NOT NULL DEFAULT 'pending',
                note       TEXT    DEFAULT '',
                created_at TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        old_conn.execute("INSERT INTO orders SELECT * FROM orders_old")
        old_conn.execute("DROP TABLE orders_old")
        
        # --- reviews ---
        old_conn.execute("ALTER TABLE reviews RENAME TO reviews_old")
        old_conn.execute("""
            CREATE TABLE reviews (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                username   TEXT    NOT NULL,
                rating     INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comment    TEXT    DEFAULT '',
                created_at TEXT    DEFAULT (datetime('now','localtime')),
                UNIQUE (product_id, username),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        old_conn.execute("INSERT INTO reviews SELECT * FROM reviews_old")
        old_conn.execute("DROP TABLE reviews_old")
        
        # --- wishlist ---
        old_conn.execute("ALTER TABLE wishlist RENAME TO wishlist_old")
        old_conn.execute("""
            CREATE TABLE wishlist (
                username   TEXT    NOT NULL,
                product_id INTEGER NOT NULL,
                added_at   TEXT    DEFAULT (datetime('now','localtime')),
                PRIMARY KEY (username, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        old_conn.execute("INSERT INTO wishlist SELECT * FROM wishlist_old")
        old_conn.execute("DROP TABLE wishlist_old")
        
        # 5. Xóa bảng users khỏi event_rental.db
        old_conn.execute("DROP TABLE users")
        
        old_conn.commit()
        old_conn.execute("PRAGMA foreign_keys = ON;")
        print("Da go bo khoa ngoai va xoa bang users khoi event_rental.db")
        
    except Exception as e:
        print("Loi migration:", e)
        old_conn.rollback()
        new_conn.rollback()
    finally:
        old_conn.close()
        new_conn.close()

if __name__ == "__main__":
    migrate()
