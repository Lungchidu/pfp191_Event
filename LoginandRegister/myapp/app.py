from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import bcrypt
import os

from database import Database
from seed_data import seed_shop_data
from ui_data import get_ui_data
from shop import (
    get_all_products,
    get_product_by_id,
    get_related_products,
    get_flash_products,
    get_locations,
    get_all_categories,
    get_cart_items,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    checkout_cart,
    filter_products,
    parse_filters_from_request,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "eventrent-dev-secret")

# ── Cookie config để session hoạt động cross-origin ──
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

SHOP_URL = os.environ.get("SHOP_URL", "http://localhost:3000")

# ── Cho phép cả port 3000 và 3001 (React tự đổi port khi bị trùng) ──
ALLOWED_ORIGINS = [
    SHOP_URL,
    "http://localhost:3000",
    "http://localhost:3001",
]

CORS(
    app,
    supports_credentials=True,
    origins=ALLOWED_ORIGINS,
)

db = Database()
db.init_tables()
seed_shop_data(db)


def get_logged_in_user():
    return session.get("username", "").strip()


def require_login():
    username = get_logged_in_user()
    if not username:
        return None
    return username


# ---------- Trang đăng nhập HTML ----------
@app.route("/")
def index():
    return render_template("index.html", shop_url=SHOP_URL)


# ---------- API phiên đăng nhập ----------
@app.route("/api/me", methods=["GET"])
def api_me():
    username = get_logged_in_user()
    if username:
        return jsonify({"success": True, "logged_in": True, "username": username})
    return jsonify({"success": True, "logged_in": False, "username": None})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("username", None)
    return jsonify({"success": True, "message": "Đã đăng xuất!"})


# ---------- API tài khoản ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Vui lòng nhập đầy đủ!"})

    conn = db.connect()
    existing = conn.execute(
        "SELECT 1 FROM users WHERE username=?", (username,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"success": False, "message": "Tài khoản đã tồn tại!"})

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Đăng ký thành công!"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = db.connect()
    row = conn.execute(
        "SELECT password FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()

    if not row or not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return jsonify({
            "success": False,
            "message": "Tài khoản hoặc mật khẩu không đúng!",
        })

    session["username"] = username
    return jsonify({
        "success": True,
        "message": f"Chào mừng {username}!",
        "username": username,
    })


# ---------- API giao diện trang chủ ----------
@app.route("/api/ui", methods=["GET"])
def api_ui():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    return jsonify({"success": True, **get_ui_data()})


# ---------- API sản phẩm ----------
@app.route("/api/products", methods=["GET"])
def api_products():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    filters = parse_filters_from_request(request.args)
    all_products = get_all_products(db)
    products = filter_products(all_products, filters)

    return jsonify({"success": True, "products": products})


@app.route("/api/products/flash", methods=["GET"])
def api_flash_products():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    return jsonify({"success": True, "products": get_flash_products(db)})


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_product_detail(product_id):
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    product = get_product_by_id(db, product_id)
    if product is None:
        return jsonify({"success": False, "message": "Không tìm thấy sản phẩm!"}), 404

    related = get_related_products(db, product_id)
    return jsonify({
        "success": True,
        "product": product,
        "related": related,
    })


@app.route("/api/categories", methods=["GET"])
def api_categories():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    return jsonify({"success": True, "categories": get_all_categories(db)})


@app.route("/api/locations", methods=["GET"])
def api_locations():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    return jsonify({"success": True, "locations": get_locations(db)})


# ---------- API giỏ hàng ----------
@app.route("/api/cart", methods=["GET"])
def api_get_cart():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    return jsonify({"success": True, "items": get_cart_items(db, username)})


@app.route("/api/cart", methods=["POST"])
def api_add_cart():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))
    days = int(data.get("days", 1))

    if not product_id:
        return jsonify({"success": False, "message": "Thiếu product_id!"}), 400

    ok, message = add_to_cart(db, username, int(product_id), quantity, days)
    if not ok:
        return jsonify({"success": False, "message": message}), 404

    return jsonify({
        "success": True,
        "message": message,
        "items": get_cart_items(db, username),
    })


@app.route("/api/cart/<int:product_id>", methods=["PATCH"])
def api_update_cart(product_id):
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    quantity = data.get("quantity")
    days = data.get("days")
    if quantity is not None:
        quantity = int(quantity)
    if days is not None:
        days = int(days)

    ok, message = update_cart_item(db, username, product_id, quantity, days)
    if not ok:
        return jsonify({"success": False, "message": message}), 404

    return jsonify({
        "success": True,
        "message": message,
        "items": get_cart_items(db, username),
    })


@app.route("/api/cart/<int:product_id>", methods=["DELETE"])
def api_delete_cart(product_id):
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    ok, message = remove_from_cart(db, username, product_id)
    return jsonify({
        "success": ok,
        "message": message,
        "items": get_cart_items(db, username),
    })


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    username = require_login()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    ok, message, total = checkout_cart(db, username)
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message, "total": total})


if __name__ == "__main__":
    app.run(debug=True)
