from database import row_to_category, row_to_product
from search_filter import filter_products, search


def parse_filters_from_request(args):
    return {
        "query": args.get("q", ""),
        "category_id": args.get("cat"),
        "location": args.get("loc", ""),
        "min_rating": args.get("rating", 0),
        "max_price": args.get("max"),
        "flash_only": args.get("flash"),
        "sort_by": args.get("sort", "default"),
    }


def get_all_products(db):
    conn = db.connect()
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return [row_to_product(row) for row in rows]


def get_product_by_id(db, product_id):
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return row_to_product(row)


def get_related_products(db, product_id, limit=4):
    product = get_product_by_id(db, product_id)
    if product is None:
        return []

    all_products = get_all_products(db)
    related = []
    for p in all_products:
        if p["id"] == product_id:
            continue
        if p["categoryId"] == product["categoryId"]:
            related.append(p)
        if len(related) >= limit:
            break
    return related


def get_flash_products(db):
    all_products = get_all_products(db)
    return [p for p in all_products if p["isFlash"]]


def get_locations(db):
    all_products = get_all_products(db)
    locations = []
    for p in all_products:
        if p["location"] not in locations:
            locations.append(p["location"])
    return locations


def get_all_categories(db):
    conn = db.connect()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [row_to_category(row) for row in rows]


def get_cart_items(db, username):
    conn = db.connect()
    rows = conn.execute(
        """
        SELECT c.product_id, c.quantity, c.days,
               p.name, p.price, p.image, p.location
        FROM cart_items c
        JOIN products p ON p.id = c.product_id
        WHERE c.username = ?
        ORDER BY c.product_id
        """,
        (username,),
    ).fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "id": row["product_id"],
            "name": row["name"],
            "price": row["price"],
            "image": row["image"],
            "location": row["location"],
            "quantity": row["quantity"],
            "days": row["days"],
        })
    return items


def calc_cart_total(items):
    total = 0
    for item in items:
        total += item["price"] * item["quantity"] * item["days"]
    return total


def add_to_cart(db, username, product_id, quantity=1, days=1):
    conn = db.connect()
    product = conn.execute(
        "SELECT id FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if product is None:
        conn.close()
        return False, "Không tìm thấy sản phẩm!"

    existing = conn.execute(
        """
        SELECT quantity, days FROM cart_items
        WHERE username = ? AND product_id = ?
        """,
        (username, product_id),
    ).fetchone()

    if existing:
        new_qty = existing["quantity"] + quantity
        new_days = max(existing["days"], days)
        conn.execute(
            """
            UPDATE cart_items
            SET quantity = ?, days = ?
            WHERE username = ? AND product_id = ?
            """,
            (new_qty, new_days, username, product_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO cart_items (username, product_id, quantity, days)
            VALUES (?, ?, ?, ?)
            """,
            (username, product_id, quantity, days),
        )

    conn.commit()
    conn.close()
    return True, "Đã thêm vào giỏ thuê"


def update_cart_item(db, username, product_id, quantity=None, days=None):
    conn = db.connect()
    row = conn.execute(
        """
        SELECT quantity, days FROM cart_items
        WHERE username = ? AND product_id = ?
        """,
        (username, product_id),
    ).fetchone()

    if row is None:
        conn.close()
        return False, "Không có sản phẩm trong giỏ!"

    new_qty = quantity if quantity is not None else row["quantity"]
    new_days = days if days is not None else row["days"]

    if new_qty <= 0:
        conn.execute(
            "DELETE FROM cart_items WHERE username = ? AND product_id = ?",
            (username, product_id),
        )
    else:
        conn.execute(
            """
            UPDATE cart_items SET quantity = ?, days = ?
            WHERE username = ? AND product_id = ?
            """,
            (new_qty, new_days, username, product_id),
        )

    conn.commit()
    conn.close()
    return True, "Đã cập nhật giỏ"


def remove_from_cart(db, username, product_id):
    conn = db.connect()
    conn.execute(
        "DELETE FROM cart_items WHERE username = ? AND product_id = ?",
        (username, product_id),
    )
    conn.commit()
    conn.close()
    return True, "Đã xóa khỏi giỏ thuê"


def _items_from_client(db, client_items):
    """Lấy thông tin sản phẩm.
    - Nếu tìm thấy trong DB: dùng giá/tên từ DB (chính xác).
    - Nếu không có trong DB (sản phẩm từ mockData): dùng dữ liệu client gửi lên
      và đặt product_id = None để tránh vi phạm FK constraint.
    """
    items = []
    for row in client_items:
        raw_id = row.get("product_id") or row.get("id")
        product_id = int(raw_id) if raw_id else None
        quantity = max(1, int(row.get("quantity", 1)))
        days = max(1, int(row.get("days", 1)))

        product = get_product_by_id(db, product_id) if product_id else None

        if product:
            items.append({
                "db_id":    product_id,
                "name":     product["name"],
                "price":    product["price"],
                "image":    product["image"],
                "location": product["location"],
                "quantity": quantity,
                "days":     days,
            })
        else:
            client_name  = row.get("name", f"Sản phẩm #{product_id}")
            client_price = int(row.get("price", 0))
            if not client_price:
                continue
            items.append({
                "db_id":    None,
                "name":     client_name,
                "price":    client_price,
                "image":    row.get("image", ""),
                "location": row.get("location", ""),
                "quantity": quantity,
                "days":     days,
            })

    if not items:
        return None, "Không có sản phẩm hợp lệ trong giỏ!"
    return items, None


def checkout_cart(db, username, client_items=None, note=""):
    """Đặt thuê: lưu đơn hàng và xóa giỏ.

    client_items: giỏ từ React (localStorage) — ưu tiên dùng khi có.
    """
    if client_items:
        items, err = _items_from_client(db, client_items)
        if err:
            return False, err, 0
    else:
        items = get_cart_items(db, username)

    if not items:
        return False, "Giỏ thuê đang trống!", 0

    total = sum(i["price"] * i["quantity"] * i["days"] for i in items)
    conn = db.connect()
    try:
        conn.execute("PRAGMA foreign_keys = OFF")

        cur = conn.execute(
            "INSERT INTO orders (username, total, note) VALUES (?, ?, ?)",
            (username, total, note or ""),
        )
        order_id = cur.lastrowid

        for item in items:
            pid = item.get("db_id")
            conn.execute(
                """
                INSERT INTO order_items
                    (order_id, product_id, product_name, price, quantity, days)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    pid,
                    item["name"],
                    item["price"],
                    item["quantity"],
                    item["days"],
                ),
            )
            
            # Cập nhật số lượng
            conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], pid))
            # Nếu số lượng hết, xóa món hàng đó
            conn.execute("DELETE FROM products WHERE id = ? AND stock <= 0", (pid,))

        conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()
        except Exception:
            pass

    return True, f"Đặt thuê thành công! Tổng: {total:,}đ", total


def get_user_orders(db, username):
    conn = db.connect()
    try:
        order_rows = conn.execute(
            "SELECT * FROM orders WHERE username = ? ORDER BY id DESC",
            (username,)
        ).fetchall()
        
        orders = []
        for row in order_rows:
            order_id = row["id"]
            item_rows = conn.execute(
                """
                SELECT oi.*, p.image, p.location
                FROM order_items oi
                LEFT JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id = ?
                """,
                (order_id,)
            ).fetchall()
            
            items = []
            for item in item_rows:
                items.append({
                    "id": item["product_id"],
                    "product_name": item["product_name"],
                    "price": item["price"],
                    "quantity": item["quantity"],
                    "days": item["days"],
                    "image": item["image"] or "",
                    "location": item["location"] or ""
                })
            
            orders.append({
                "id": f"EVR-2026-{order_id:03d}",
                "db_id": order_id,
                "total": row["total"],
                "status": row["status"],
                "note": row["note"],
                "created_at": row["created_at"],
                "items": items
            })
        return orders
    finally:
        conn.close()
