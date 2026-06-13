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
    """Lấy giá từ database theo danh sách React gửi lên."""
    items = []
    for row in client_items:
        product_id = int(row.get("product_id") or row.get("id"))
        quantity = max(1, int(row.get("quantity", 1)))
        days = max(1, int(row.get("days", 1)))
        product = get_product_by_id(db, product_id)
        if product is None:
            return None, f"Không tìm thấy sản phẩm #{product_id}!"
        items.append({
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "image": product["image"],
            "location": product["location"],
            "quantity": quantity,
            "days": days,
        })
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

    if len(items) == 0:
        return False, "Giỏ thuê đang trống!", 0

    total = calc_cart_total(items)
    conn = db.connect()
    try:
        cur = conn.execute(
            "INSERT INTO orders (username, total, note) VALUES (?, ?, ?)",
            (username, total, note or ""),
        )
        order_id = cur.lastrowid
        for item in items:
            conn.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, product_name, price, quantity, days)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["id"],
                    item["name"],
                    item["price"],
                    item["quantity"],
                    item["days"],
                ),
            )
        conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))
        conn.commit()
    finally:
        conn.close()
    return True, f"Đặt thuê thành công! Tổng: {total:,}đ", total
