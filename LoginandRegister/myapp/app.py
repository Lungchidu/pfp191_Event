from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import bcrypt
import os
import sys
import jwt
import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import Database
from seed_data import seed_all
from ui_data import get_ui_data
from shipper_routes import shipper_bp
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
app.secret_key = os.environ.get("SECRET_KEY", "eventrent-secret-2026")
SECRET_KEY = app.secret_key

SHOP_URL = os.environ.get("SHOP_URL", "http://localhost:3000")


def get_shop_url():
    """URL React shop — ưu tiên ?shop_url= từ query (khi React chạy port 3002...)."""
    return request.args.get("shop_url", SHOP_URL).rstrip("/")

CORS(app, origins="*", supports_credentials=True)
app.register_blueprint(shipper_bp)

db = Database()
db.init_tables()
seed_all(db)


def get_username_from_request():
    """Lấy username từ header, JSON body hoặc query string."""
    username = request.headers.get("X-Username", "")
    if username:
        return username.strip()
    data = request.get_json(silent=True) or {}
    username = data.get("username") or request.args.get("username", "")
    return username.strip()


@app.route("/")
def index():
    return render_template("index.html", shop_url=get_shop_url())


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
        return jsonify({"success": False, "message": "Tài khoản đã tồn tại"})

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Đăng ký thành công"})


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

    if not row or not bcrypt.checkpw(password.encode(), row[0].encode()):
        return jsonify({
            "success": False,
            "message": "Nhập sai tên tài khoản hoặc mật khẩu",
        })

    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "success": True,
        "message": f"Chào mừng {username}!",
        "username": username,
        "token": token,
    })


@app.route("/verify", methods=["POST"])
def verify():
    data = request.json or {}
    token = data.get("token", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"success": True, "username": payload["username"]})
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Token đã hết hạn!"})
    except Exception:
        return jsonify({"success": False, "message": "Token không hợp lệ!"})


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"success": True, "service": "EventRent API"})


@app.route("/api/ui", methods=["GET"])
def api_ui():
    return jsonify({"success": True, **get_ui_data()})


@app.route("/api/products", methods=["GET"])
def api_products():
    products = get_all_products(db)
    f = parse_filters_from_request(request.args)
    filtered = filter_products(
        products,
        keyword=f.get("query") or None,
        max_price=f.get("max_price"),
        location=f.get("location") or None,
        category_id=f.get("category_id"),
        min_rating=f.get("min_rating") or None,
        flash_only=f.get("flash_only"),
        sort_by=f.get("sort_by") if f.get("sort_by") != "default" else None,
    )
    return jsonify({"success": True, "products": filtered})


@app.route("/api/products/flash", methods=["GET"])
def api_flash_products():
    products = get_flash_products(db)
    return jsonify({"success": True, "products": products})


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_product_detail(product_id):
    product = get_product_by_id(db, product_id)
    if product is None:
        return jsonify({"success": False, "message": "Không tìm thấy sản phẩm!"}), 404
    related = get_related_products(db, product_id)
    return jsonify({"success": True, "product": product, "related": related})


@app.route("/api/categories", methods=["GET"])
def api_categories():
    categories = get_all_categories(db)
    return jsonify({"success": True, "categories": categories})


@app.route("/api/locations", methods=["GET"])
def api_locations():
    locations = get_locations(db)
    return jsonify({"success": True, "locations": locations})


@app.route("/api/cart", methods=["GET"])
def api_get_cart():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    items = get_cart_items(db, username)
    return jsonify({"success": True, "items": items})


@app.route("/api/cart", methods=["POST"])
def api_add_cart():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))
    days = int(data.get("days", 1))

    ok, message = add_to_cart(db, username, product_id, quantity, days)
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    items = get_cart_items(db, username)
    return jsonify({"success": True, "message": message, "items": items})


@app.route("/api/cart/<int:product_id>", methods=["PATCH"])
def api_update_cart(product_id):
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    ok, message = update_cart_item(
        db,
        username,
        product_id,
        quantity=data.get("quantity"),
        days=data.get("days"),
    )
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    items = get_cart_items(db, username)
    return jsonify({"success": True, "message": message, "items": items})


@app.route("/api/cart/<int:product_id>", methods=["DELETE"])
def api_remove_cart(product_id):
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    ok, message = remove_from_cart(db, username, product_id)
    items = get_cart_items(db, username)
    return jsonify({"success": True, "message": message, "items": items})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    client_items = data.get("items")
    note = data.get("note", "")

    ok, message, total = checkout_cart(
        db, username, client_items=client_items, note=note
    )
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message, "total": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
