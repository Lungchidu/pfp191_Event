from database import row_to_category, row_to_product


def filter_products(products, filters):
    """Lọc sản phẩm — logic chạy trên Python (không còn trong JavaScript)."""
    query = (filters.get("query") or "").strip().lower()
    category_id = filters.get("category_id")
    location = filters.get("location") or ""
    min_rating = float(filters.get("min_rating") or 0)
    max_price = filters.get("max_price")
    flash_only = filters.get("flash_only") in (True, "1", "true", 1)
    sort_by = filters.get("sort_by") or "default"

    result = []
    for p in products:
        if flash_only and not p["isFlash"]:
            continue
        if category_id is not None and category_id != "":
            if p["categoryId"] != int(category_id):
                continue
        if location and p["location"] != location:
            continue
        if p["rating"] < min_rating:
            continue
        if max_price is not None and max_price != "":
            if p["price"] > int(max_price):
                continue

        if query:
            haystack = " ".join([
                p["name"],
                p["description"],
                p["location"],
                *p.get("tags", []),
            ]).lower()
            if query not in haystack:
                continue

        result.append(p)

    if sort_by == "price-asc":
        result.sort(key=lambda x: x["price"])
    elif sort_by == "price-desc":
        result.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        result.sort(key=lambda x: x["rating"], reverse=True)

    return result


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


def checkout_cart(db, username):
    """Đặt thuê: lưu đơn hàng và xóa giỏ."""
    items = get_cart_items(db, username)
    if len(items) == 0:
        return False, "Giỏ thuê đang trống!", 0

    total = calc_cart_total(items)
    conn = db.connect()
    conn.execute(
        "INSERT INTO orders (username, total) VALUES (?, ?)",
        (username, total),
    )
    conn.execute("DELETE FROM cart_items WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True, f"Đặt thuê thành công! Tổng: {total:,}đ", total
