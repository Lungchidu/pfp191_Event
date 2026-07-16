"""
database.py  –  EventRent unified SQLite manager (OOP Refactored)
=================================================================
Kiến trúc 3 database:
  • products.db   → Chứa bảng categories và products (sản phẩm/danh mục)
  • event_rental.db → Chứa bảng cart_items, orders, order_items, reviews, wishlist
  • customers.db  → Chứa bảng users (tài khoản đăng nhập)

Áp dụng đầy đủ 4 trụ cột OOP:

  1. Đóng gói (Encapsulation):
     - Thuộc tính `_db_file` là protected, truy cập qua property `db_path`.
     - Các method nội bộ `_execute_pragmas()` bắt đầu bằng `_` (private convention).

  2. Trừu tượng (Abstraction):
     - `BaseDatabase` kế thừa ABC, khai báo @abstractmethod `init_tables()`.
     - Bắt buộc mọi class con phải tự định nghĩa init_tables().

  3. Kế thừa (Inheritance):
     - ProductDatabase(BaseDatabase), Database(BaseDatabase), CustomerDatabase(BaseDatabase)
     - Tái sử dụng connect(), connect_readonly() từ lớp cha.

  4. Đa hình (Polymorphism):
     - Mỗi class con override init_tables() với logic SQL riêng.
     - Có thể gọi db.init_tables() trên bất kỳ instance nào mà không cần biết loại DB.
"""

import json
import os
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# Cấu hình đường dẫn
# ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, "event_rental.db")
CUSTOMER_DB_FILE = os.path.join(BASE_DIR, "customers.db")
PRODUCT_DB_FILE  = os.path.join(BASE_DIR, "products.db")


# ──────────────────────────────────────────────────────────────
# Lớp cha trừu tượng: BaseDatabase (Abstract Base Class)
# ──────────────────────────────────────────────────────────────
class BaseDatabase(ABC):
    """Lớp cha trừu tượng cho tất cả các database manager.

    Đóng gói (Encapsulation):
        - `_db_file` là thuộc tính protected, truy cập qua property `db_path`.
        - `_execute_pragmas()` là method nội bộ, không gọi từ bên ngoài.

    Trừu tượng (Abstraction):
        - Kế thừa ABC, khai báo @abstractmethod `init_tables()`.
        - Cung cấp interface chung: connect(), connect_readonly().
        - Ẩn đi chi tiết kết nối SQLite, PRAGMA, URI mode bên trong.

    Kế thừa (Inheritance):
        - Các class con (ProductDatabase, Database, CustomerDatabase) kế thừa
          toàn bộ logic kết nối mà không cần viết lại.

    Đa hình (Polymorphism):
        - Mỗi class con override init_tables() với logic SQL riêng.
    """

    def __init__(self, db_file: str):
        self._db_file = db_file    # ← Đóng gói: thuộc tính protected

    @property
    def db_path(self) -> str:
        """Trả về đường dẫn database file (read-only property).
        Đóng gói: chỉ cho phép đọc, không cho phép gán trực tiếp."""
        return self._db_file

    def _execute_pragmas(self, conn: sqlite3.Connection) -> None:
        """Thiết lập PRAGMA mặc định cho kết nối.
        Đóng gói: method nội bộ, bắt đầu bằng `_` (private convention)."""
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

    def connect(self, create_if_missing: bool = False) -> sqlite3.Connection:
        """Kết nối Read-Write đến database.
        Trừu tượng: ẩn đi chi tiết URI mode, PRAGMA config bên trong."""
        if create_if_missing:
            conn = sqlite3.connect(self._db_file)
        else:
            uri = f"file:{self._db_file}?mode=rw"
            conn = sqlite3.connect(uri, uri=True)

        conn.row_factory = sqlite3.Row
        self._execute_pragmas(conn)
        return conn

    def connect_readonly(self) -> sqlite3.Connection:
        """Kết nối Read-Only đến database.
        Nếu file chưa tồn tại sẽ báo lỗi thay vì tự tạo file rỗng."""
        uri = f"file:{self._db_file}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    @abstractmethod
    def init_tables(self, create_if_missing: bool = False) -> None:
        """Khởi tạo các bảng trong database.
        Trừu tượng: @abstractmethod — bắt buộc mọi class con phải tự định nghĩa.
        Đa hình: mỗi class con sẽ override với logic SQL riêng."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} db='{os.path.basename(self._db_file)}'>"


# ──────────────────────────────────────────────────────────────
# Lớp con: ProductDatabase – Riêng cho sản phẩm & danh mục
# ──────────────────────────────────────────────────────────────
class ProductDatabase(BaseDatabase):
    """Quản lý kết nối SQLite riêng cho sản phẩm và danh mục.

    Kế thừa (Inheritance):
        - Tái sử dụng connect(), connect_readonly(), _execute_pragmas() từ BaseDatabase.

    Đa hình (Polymorphism):
        - Override init_tables() với logic tạo bảng categories và products.
    """

    def __init__(self, db_file: str = PRODUCT_DB_FILE):
        super().__init__(db_file)    # ← Kế thừa: gọi __init__ của BaseDatabase

    def init_tables(self, create_if_missing: bool = False) -> None:
        """Đa hình: Override init_tables() — tạo bảng categories và products."""
        conn = self.connect(create_if_missing=create_if_missing)
        try:
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
                    tags           TEXT    NOT NULL DEFAULT '[]',
                    image          TEXT    NOT NULL DEFAULT '',
                    specs          TEXT    NOT NULL DEFAULT '[]',
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
                pass  # Column already exists

            conn.commit()
        finally:
            conn.close()


# ──────────────────────────────────────────────────────────────
# Lớp con: Database – Đơn hàng, giỏ hàng, đánh giá, wishlist
# ──────────────────────────────────────────────────────────────
class Database(BaseDatabase):
    """Quản lý kết nối SQLite cho event_rental.db (đơn hàng, giỏ, reviews).

    Kế thừa (Inheritance):
        - Tái sử dụng connect(), connect_readonly() từ BaseDatabase.

    Đa hình (Polymorphism):
        - Override init_tables() với logic tạo bảng cart, orders, reviews, wishlist.
    """

    def __init__(self, db_file: str = DB_FILE):
        super().__init__(db_file)    # ← Kế thừa: gọi __init__ của BaseDatabase

    def init_tables(self, create_if_missing: bool = False) -> None:
        """Đa hình: Override init_tables() — tạo bảng cart, orders, reviews, wishlist."""
        conn = self.connect(create_if_missing=create_if_missing)
        try:
            # ── Giỏ hàng ──────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cart_items (
                    username   TEXT    NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity   INTEGER NOT NULL DEFAULT 1,
                    days       INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (username, product_id)
                )
            """)

            # ── Đơn hàng (header) ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL,
                    total         INTEGER NOT NULL DEFAULT 0,
                    status        TEXT    NOT NULL DEFAULT 'completed',
                    note          TEXT    DEFAULT '',
                    delivery_date TEXT    DEFAULT '',
                    created_at    TEXT    DEFAULT (datetime('now','localtime'))
                )
            """)

            # Migration: add delivery_date to existing orders table if not exists
            try:
                conn.execute("ALTER TABLE orders ADD COLUMN delivery_date TEXT DEFAULT ''")
            except Exception:
                pass  # Column already exists

            # ── Chi tiết đơn hàng ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id     INTEGER NOT NULL,
                    product_id   INTEGER,
                    product_name TEXT    NOT NULL,
                    price        INTEGER NOT NULL,
                    quantity     INTEGER NOT NULL DEFAULT 1,
                    days         INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
                )
            """)

            # ── Đánh giá sản phẩm ─────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    username   TEXT    NOT NULL,
                    rating     INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                    comment    TEXT    DEFAULT '',
                    created_at TEXT    DEFAULT (datetime('now','localtime')),
                    UNIQUE (product_id, username)
                )
            """)

            # ── Danh sách yêu thích ───────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wishlist (
                    username   TEXT    NOT NULL,
                    product_id INTEGER NOT NULL,
                    added_at   TEXT    DEFAULT (datetime('now','localtime')),
                    PRIMARY KEY (username, product_id)
                )
            """)

            conn.commit()
        finally:
            conn.close()


# ──────────────────────────────────────────────────────────────
# Lớp con: CustomerDatabase
# ──────────────────────────────────────────────────────────────
class CustomerDatabase(BaseDatabase):
    """Quản lý kết nối SQLite riêng cho khách hàng.

    Kế thừa (Inheritance):
        - Tái sử dụng connect(), connect_readonly() từ BaseDatabase.

    Đa hình (Polymorphism):
        - Override init_tables() với logic tạo bảng users.
    """

    def __init__(self, db_file: str = CUSTOMER_DB_FILE):
        super().__init__(db_file)    # ← Kế thừa: gọi __init__ của BaseDatabase

    def init_tables(self, create_if_missing: bool = False) -> None:
        """Đa hình: Override init_tables() — tạo bảng users."""
        conn = self.connect(create_if_missing=create_if_missing)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username   TEXT PRIMARY KEY,
                    password   TEXT    NOT NULL,
                    email      TEXT    DEFAULT '',
                    full_name  TEXT    DEFAULT '',
                    phone      TEXT    DEFAULT '',
                    birth_year INTEGER DEFAULT 0,
                    address    TEXT    DEFAULT '',
                    role       TEXT    DEFAULT 'customer',
                    is_active  INTEGER DEFAULT 1,
                    created_at TEXT    DEFAULT (datetime('now','localtime'))
                )
            """)
            # Migration: add birth_year and address to existing users table if not exists
            try:
                conn.execute("ALTER TABLE users ADD COLUMN birth_year INTEGER DEFAULT 0")
            except Exception:
                pass
            try:
                conn.execute("ALTER TABLE users ADD COLUMN address TEXT DEFAULT ''")
            except Exception:
                pass
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
    d = dict(row)
    return {
        "username":  d.get("username"),
        "email":     d.get("email"),
        "fullName":  d.get("full_name", ""),
        "phone":     d.get("phone", ""),
        "birthYear": d.get("birth_year", 0),
        "address":    d.get("address", ""),
        "role":      d.get("role"),
        "isActive":  bool(d.get("is_active")),
        "createdAt": d.get("created_at"),
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
