import json
import os
import sqlite3

# File database nằm cùng thư mục với app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "event_rental.db")


class Database:
    """Lớp đơn giản quản lý kết nối SQLite (OOP cơ bản)."""

    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    def connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        conn = self.connect()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                icon TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                original_price INTEGER NOT NULL,
                discount INTEGER NOT NULL,
                sold INTEGER NOT NULL,
                stock INTEGER NOT NULL,
                rating REAL NOT NULL,
                location TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                is_flash INTEGER NOT NULL,
                tags TEXT NOT NULL,
                image TEXT NOT NULL,
                specs TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                username TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                days INTEGER NOT NULL,
                PRIMARY KEY (username, product_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                total INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()


def row_to_product(row):
    """Chuyển 1 dòng SQLite thành dict cho React đọc."""
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "price": row["price"],
        "originalPrice": row["original_price"],
        "discount": row["discount"],
        "sold": row["sold"],
        "stock": row["stock"],
        "rating": row["rating"],
        "location": row["location"],
        "categoryId": row["category_id"],
        "isFlash": bool(row["is_flash"]),
        "tags": json.loads(row["tags"]),
        "image": row["image"],
        "specs": json.loads(row["specs"]),
    }


def row_to_category(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "icon": row["icon"],
    }
