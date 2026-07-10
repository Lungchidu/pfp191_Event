import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "event_rental.db")

def fix():
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("PRAGMA foreign_keys = OFF;")
        
        # 1. order_items
        conn.execute("ALTER TABLE order_items RENAME TO order_items_broken;")
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
            FROM order_items_broken
        """)
        conn.execute("DROP TABLE order_items_broken;")
        
        conn.commit()
        print("Fixed order_items schema.")
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix()
