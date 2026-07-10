"""
database.py  –  EventRent unified SQLite manager
=================================================
Gộp users.db (auth) và event_rental.db (shop) thành một file DB duy nhất.
Tương thích ngược với app.py (Flask auth) và shop.py (product/cart/order).

Thay đổi chính so với phiên bản cũ:
  • Một file DB duy nhất: event_rental.db
  • Bảng users có thêm: email, full_name, phone, role, created_at, is_active
  • Bảng products có thêm: created_at, updated_at
  • Bảng orders có thêm: status, note
  • Bảng mới: order_items (chi tiết từng dòng trong đơn hàng)
  • Bảng mới: reviews (đánh giá sản phẩm)
  • Bảng mới: wishlist (sản phẩm yêu thích)
  • Tất cả câu lệnh dùng parameterized query – an toàn SQL injection
"""

import json
import os
import sqlite3
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Cấu hình đường dẫn
# ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, "event_rental.db")
CUSTOMER_DB_FILE = os.path.join(BASE_DIR, "customers.db")


# ──────────────────────────────────────────────────────────────
# Lớp Database
# ──────────────────────────────────────────────────────────────
class Database:
    """Quản lý kết nối SQLite dùng chung cho toàn ứng dụng."""

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file

    # ── kết nối ──────────────────────────────────────────────
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")   # bật ràng buộc FK
        conn.execute("PRAGMA journal_mode = WAL")  # tốt hơn cho nhiều reader
        return conn

    # ── khởi tạo schema ──────────────────────────────────────
    def init_tables(self) -> None:
        conn = self.connect()
        try:
            # ── Tài khoản người dùng (đã chuyển sang customers.db) ──

            # ── Danh mục sản phẩm ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id   INTEGER PRIMARY KEY,
                    name TEXT    NOT NULL,
                    icon TEXT    NOT NULL
                )
            """)

            # ── Sản phẩm ──────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id             INTEGER PRIMARY KEY,
                    name           TEXT    NOT NULL,
                    name_en        TEXT    DEFAULT '',
                    description    TEXT    NOT NULL DEFAULT '',
                    description_en TEXT    DEFAULT '',
                    price          INTEGER NOT NULL DEFAULT 0,
                    original_price INTEGER NOT NULL DEFAULT 0,
                    discount       INTEGER NOT NULL DEFAULT 0,
                    sold           INTEGER NOT NULL DEFAULT 0,
                    stock          INTEGER NOT NULL DEFAULT 0,
                    rating         REAL    NOT NULL DEFAULT 5.0,
                    location       TEXT    NOT NULL DEFAULT '',
                    category_id    INTEGER NOT NULL DEFAULT 1,
                    is_flash       INTEGER NOT NULL DEFAULT 0,
                    tags           TEXT    NOT NULL DEFAULT '[]',   -- JSON array
                    image          TEXT    NOT NULL DEFAULT '',
                    specs          TEXT    NOT NULL DEFAULT '[]',   -- JSON array
                    created_at     TEXT    DEFAULT (datetime('now','localtime')),
                    updated_at     TEXT    DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            # Migration: add name_en and description_en to existing products table if not exists
            try:
                conn.execute("ALTER TABLE products ADD COLUMN name_en TEXT DEFAULT ''")
                conn.execute("ALTER TABLE products ADD COLUMN description_en TEXT DEFAULT ''")
            except Exception:
                pass # Column already exists

            # ── Giỏ hàng ──────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cart_items (
                    username   TEXT    NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity   INTEGER NOT NULL DEFAULT 1,
                    days       INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (username, product_id),
                    FOREIGN KEY (product_id) REFERENCES products(id)      ON DELETE CASCADE
                )
            """)

            # ── Đơn hàng (header) ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL,
                    total         INTEGER NOT NULL DEFAULT 0,
                    status        TEXT    NOT NULL DEFAULT 'pending',
                    note          TEXT    DEFAULT '',
                    delivery_date TEXT    DEFAULT '',
                    created_at    TEXT    DEFAULT (datetime('now','localtime'))
                )
            """)
            
            # Migration: add delivery_date to existing orders table if not exists
            try:
                conn.execute("ALTER TABLE orders ADD COLUMN delivery_date TEXT DEFAULT ''")
            except Exception:
                pass # Column already exists

            # ── Chi tiết đơn hàng ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id     INTEGER NOT NULL,
                    product_id   INTEGER,           -- nullable: sản phẩm có thể bị xóa
                    product_name TEXT    NOT NULL,   -- snapshot tên lúc đặt
                    price        INTEGER NOT NULL,   -- snapshot giá lúc đặt
                    quantity     INTEGER NOT NULL DEFAULT 1,
                    days         INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)

            # ── Migration: nếu bảng cũ có product_id NOT NULL → recreate ──────
            col_info = conn.execute("PRAGMA table_info(order_items)").fetchall()
            pid_col = next((c for c in col_info if c["name"] == "product_id"), None)
            if pid_col and pid_col["notnull"] == 1:
                conn.execute("ALTER TABLE order_items RENAME TO order_items_old")
                conn.execute("""
                    CREATE TABLE order_items (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id     INTEGER NOT NULL,
                        product_id   INTEGER,
                        product_name TEXT    NOT NULL,
                        price        INTEGER NOT NULL,
                        quantity     INTEGER NOT NULL DEFAULT 1,
                        days         INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                    )
                """)
                conn.execute("""
                    INSERT INTO order_items
                        (id, order_id, product_id, product_name, price, quantity, days)
                    SELECT id, order_id, product_id, product_name, price, quantity, days
                    FROM order_items_old
                """)
                conn.execute("DROP TABLE order_items_old")

            # ── Đánh giá sản phẩm ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
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

            # ── Danh sách yêu thích ───────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    username   TEXT    NOT NULL,
                    product_id INTEGER NOT NULL,
                    added_at   TEXT    DEFAULT (datetime('now','localtime')),
                    PRIMARY KEY (username, product_id),
                    FOREIGN KEY (product_id) REFERENCES products(id)     ON DELETE CASCADE
                )
            """)

            conn.commit()
        finally:
            conn.close()


# ──────────────────────────────────────────────────────────────
# Lớp CustomerDatabase
# ──────────────────────────────────────────────────────────────
class CustomerDatabase:
    """Quản lý kết nối SQLite riêng cho khách hàng."""

    def __init__(self, db_file: str = CUSTOMER_DB_FILE):
        self.db_file = db_file

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def init_tables(self) -> None:
        conn = self.connect()
        try:
            conn.execute("""
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
            conn.commit()
        finally:
            conn.close()

# ──────────────────────────────────────────────────────────────
# Helper: chuyển Row → dict
# ──────────────────────────────────────────────────────────────
def row_to_product(row: sqlite3.Row) -> dict:
    d = dict(row)
    return {
        "id":            d.get("id"),
        "name":          d.get("name"),
        "name_en":       d.get("name_en", ""),
        "description":   d.get("description"),
        "description_en":d.get("description_en", ""),
        "price":         d.get("price"),
        "originalPrice": d.get("original_price"),
        "discount":      d.get("discount"),
        "sold":          d.get("sold"),
        "stock":         d.get("stock"),
        "rating":        d.get("rating"),
        "location":      d.get("location"),
        "categoryId":    d.get("category_id"),
        "isFlash":       bool(d.get("is_flash", 0)),
        "tags":          json.loads(d.get("tags") or '[]'),
        "image":         d.get("image"),
        "specs":         json.loads(d.get("specs") or '[]'),
        "createdAt":     d.get("created_at"),
        "updatedAt":     d.get("updated_at"),
    }


def row_to_category(row: sqlite3.Row) -> dict:
    return {
        "id":   row["id"],
        "name": row["name"],
        "icon": row["icon"],
    }


def row_to_user(row: sqlite3.Row) -> dict:
    """Trả về thông tin user – KHÔNG bao gồm password."""
    return {
        "username":  row["username"],
        "email":     row["email"],
        "fullName":  row["full_name"],
        "phone":     row["phone"],
        "role":      row["role"],
        "isActive":  bool(row["is_active"]),
        "createdAt": row["created_at"],
    }


def row_to_order(row: sqlite3.Row) -> dict:
    d = dict(row)
    return {
        "id":        d.get("id"),
        "username":  d.get("username"),
        "total":     d.get("total"),
        "status":    d.get("status"),
        "note":      d.get("note"),
        "deliveryDate": d.get("delivery_date", ""),
        "createdAt": d.get("created_at"),
    }
