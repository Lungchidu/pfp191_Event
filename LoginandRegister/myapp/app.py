from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import bcrypt
import os
import sys
import jwt
import datetime
from deep_translator import GoogleTranslator

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import Database, CustomerDatabase, ProductDatabase
from models import User, Customer, Admin
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
    get_user_orders,
    filter_products,
    parse_filters_from_request,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "eventrent-secret-2026")
app.config["JSON_AS_ASCII"] = False   # trả về UTF-8 tiếng Việt đúng chuẩn
SECRET_KEY = app.secret_key

SHOP_URL = os.environ.get("SHOP_URL", "http://localhost:3000")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask import send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except NotFound:
        return jsonify({"success": False, "message": "Hình ảnh không tồn tại!"}), 404

def get_shop_url():
    """URL React shop — ưu tiên ?shop_url= từ query (khi React chạy port 3002...)."""
    return request.args.get("shop_url", SHOP_URL).rstrip("/")

CORS(app, origins="*", supports_credentials=True)
app.register_blueprint(shipper_bp)

product_db = ProductDatabase()
db = Database()
customer_db = CustomerDatabase()

# Auto-run migrations
product_db.init_tables()
db.init_tables()
customer_db.init_tables()

import sqlite3

def get_role_from_request():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get("role", "customer")
        except Exception:
            pass
    # Đối với yêu cầu kiểm thử hoặc gọi từ frontend chưa có JWT nhưng có lưu role trong header
    # Ở đây chúng ta chỉ dùng JWT để bảo mật chắc chắn role admin
    return "customer"

@app.errorhandler(sqlite3.OperationalError)
def handle_db_error(e):
    role = get_role_from_request()
    if role == "admin":
        return jsonify({"success": False, "message": f"[ADMIN VIEW] Lỗi Database: {str(e)}"}), 500
    
    return jsonify({
        "success": False, 
        "maintenance": True, 
        "message": "Hệ thống đang bảo trì, vui lòng thử lại sau ít phút"
    }), 500


def get_username_from_request():
    """Lấy username từ header (Authorization, X-Username), JSON body hoặc query string."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get("username", "")
        except Exception:
            pass

    username = request.headers.get("X-Username", "")
    if username:
        return username.strip()
    
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        username = request.form.get("username", "")
    else:
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

    conn = customer_db.connect()
    existing = conn.execute(
        "SELECT 1 FROM users WHERE username=?", (username,)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "Tài khoản đã tồn tại"})

    # OOP: Khởi tạo đối tượng Customer và sử dụng tính đóng gói
    new_user = Customer(username=username)
    new_user.set_password(password)
    
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (new_user.username, new_user._password, new_user.role),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Đăng ký thành công"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = customer_db.connect()
    row = conn.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()

    # OOP: Đa hình - tự động trả về Customer hoặc Admin tùy theo db
    user = User.from_db_row(dict(row) if row else None)

    # OOP: Trừu tượng - login ẩn chi tiết hash/verify bcrypt
    if not user or not user.login(password):
        return jsonify({
            "success": False,
            "message": "Nhập sai tên tài khoản hoặc mật khẩu",
        })

    token = jwt.encode({
        "username": user.username,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }, SECRET_KEY, algorithm="HS256")

    # OOP: Đa hình - Admin.to_dict() trả về nhiều data hơn Customer.to_dict()
    user_data = user.to_dict()

    return jsonify({
        "success": True,
        "message": f"Chào mừng {user.username}!",
        "username": user.username,
        "role": user.role,
        "user_data": user_data,
        "token": token,
    })


@app.route("/verify", methods=["POST"])
def verify():
    data = request.json or {}
    token = data.get("token", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"success": True, "username": payload["username"], "role": payload.get("role", "customer")})
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Token đã hết hạn!"})
    except Exception:
        return jsonify({"success": False, "message": "Token không hợp lệ!"})


@app.route("/api/profile", methods=["GET"])
def api_get_profile():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    
    conn = customer_db.connect()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if not row:
        return jsonify({"success": False, "message": "Không tìm thấy người dùng!"}), 404
        
    user = User.from_db_row(dict(row))
    return jsonify({"success": True, "profile": user.to_dict()})


@app.route("/api/profile", methods=["POST"])
def api_update_profile():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
        
    data = request.json or {}
    fullName = data.get("fullName", "").strip()
    phone = data.get("phone", "").strip()
    birthYear = data.get("birthYear")
    address = data.get("address", "").strip()
    
    if birthYear is not None:
        try:
            birthYear = int(birthYear)
        except ValueError:
            birthYear = 0
    else:
        birthYear = 0

    conn = customer_db.connect()
    try:
        conn.execute(
            """
            UPDATE users 
            SET full_name = ?, phone = ?, birth_year = ?, address = ?
            WHERE username = ?
            """,
            (fullName, phone, birthYear, address, username)
        )
        conn.commit()
        
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        user = User.from_db_row(dict(row))
        return jsonify({"success": True, "message": "Cập nhật thông tin thành công!", "profile": user.to_dict()})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"success": True, "service": "EventRent API"})


@app.route("/api/ui", methods=["GET"])
def api_ui():
    return jsonify({"success": True, **get_ui_data()})


@app.route("/api/products", methods=["GET"])
def api_products():
    products = get_all_products(product_db)
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
    products = get_flash_products(product_db)
    return jsonify({"success": True, "products": products})


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_product_detail(product_id):
    product = get_product_by_id(product_db, product_id)
    if product is None:
        return jsonify({"success": False, "message": "Không tìm thấy sản phẩm!"}), 404
    related = get_related_products(product_db, product_id)
    return jsonify({"success": True, "product": product, "related": related})


@app.route("/api/categories", methods=["GET"])
def api_categories():
    categories = get_all_categories(product_db)
    return jsonify({"success": True, "categories": categories})


@app.route("/api/locations", methods=["GET"])
def api_locations():
    locations = get_locations(product_db)
    return jsonify({"success": True, "locations": locations})


@app.route("/api/cart", methods=["GET"])
def api_get_cart():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    items = get_cart_items(db, product_db, username)
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

    ok, message = add_to_cart(db, product_db, username, product_id, quantity, days)
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    items = get_cart_items(db, product_db, username)
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

    items = get_cart_items(db, product_db, username)
    return jsonify({"success": True, "message": message, "items": items})


@app.route("/api/cart/<int:product_id>", methods=["DELETE"])
def api_remove_cart(product_id):
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    ok, message = remove_from_cart(db, username, product_id)
    items = get_cart_items(db, product_db, username)
    return jsonify({"success": True, "message": message, "items": items})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401

    data = request.json or {}
    client_items = data.get("items")
    note = data.get("note", "")

    # Sync checkout information back to user profile
    fullName = data.get("fullName")
    phone = data.get("phone")
    birthYear = data.get("birthYear")
    address = data.get("address")
    
    if fullName is not None or phone is not None or birthYear is not None or address is not None:
        conn = customer_db.connect()
        try:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if row:
                updated_fullName = fullName if fullName is not None else row["full_name"]
                updated_phone = phone if phone is not None else row["phone"]
                updated_address = address if address is not None else row["address"]
                try:
                    updated_birthYear = int(birthYear) if birthYear is not None else row["birth_year"]
                except ValueError:
                    updated_birthYear = row["birth_year"]
                
                conn.execute(
                    """
                    UPDATE users 
                    SET full_name = ?, phone = ?, birth_year = ?, address = ?
                    WHERE username = ?
                    """,
                    (updated_fullName, updated_phone, updated_birthYear, updated_address, username)
                )
                conn.commit()
        except Exception as e:
            print("Failed to sync checkout profile:", e)
        finally:
            conn.close()

    ok, message, total = checkout_cart(
        db, product_db, username, client_items=client_items, note=note
    )
    if not ok:
        return jsonify({"success": False, "message": message}), 400

    return jsonify({"success": True, "message": message, "total": total})


@app.route("/api/orders", methods=["GET"])
def api_get_orders():
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Chưa đăng nhập!"}), 401
    orders = get_user_orders(db, product_db, username)
    return jsonify({"success": True, "orders": orders})


@app.route("/api/products/<int:product_id>/reviews", methods=["GET"])
def api_get_reviews(product_id):
    # Lấy reviews từ event_rental.db
    conn = db.connect()
    rows = conn.execute(
        """
        SELECT id, username, rating, comment, created_at
        FROM reviews
        WHERE product_id = ?
        ORDER BY created_at DESC
        """,
        (product_id,)
    ).fetchall()
    conn.close()

    # Lấy ảnh sản phẩm từ products.db
    product = get_product_by_id(product_db, product_id)
    product_image = product["image"] if product else ""

    reviews = [
        {
            "id": row["id"],
            "username": row["username"],
            "rating": row["rating"],
            "comment": row["comment"],
            "createdAt": row["created_at"],
            "productImage": product_image,
        }
        for row in rows
    ]
    return jsonify({"success": True, "reviews": reviews})


@app.route("/api/products/<int:product_id>/reviews", methods=["POST"])
def api_post_review(product_id):
    username = get_username_from_request()
    if not username:
        return jsonify({"success": False, "message": "Bạn cần đăng nhập để bình luận!"}), 401

    # Kiểm tra xem user đã thuê và đơn hàng đã giao thành công (status = 'completed') chưa
    conn = db.connect()
    purchased = conn.execute(
        """
        SELECT 1 FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.username = ? AND oi.product_id = ? AND o.status = 'completed'
        LIMIT 1
        """,
        (username, product_id)
    ).fetchone()

    if not purchased:
        conn.close()
        return jsonify({"success": False, "message": "Bạn cần phải nhận được hàng (đơn hàng đã giao thành công) mới có thể bình luận!"}), 403

    data = request.json or {}
    rating = data.get("rating")
    comment = data.get("comment", "").strip()

    if not rating or not (1 <= int(rating) <= 5):
        conn.close()
        return jsonify({"success": False, "message": "Vui lòng chọn số sao từ 1–5!"}), 400

    if not comment:
        conn.close()
        return jsonify({"success": False, "message": "Vui lòng nhập nội dung bình luận!"}), 400

    try:
        conn.execute(
            """
            INSERT INTO reviews (product_id, username, rating, comment)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, username, int(rating), comment)
        )

        # Tính toán lại rating trung bình và cập nhật vào products.db
        avg_row = conn.execute(
            "SELECT AVG(rating) FROM reviews WHERE product_id = ?",
            (product_id,)
        ).fetchone()
        
        if avg_row and avg_row[0] is not None:
            new_avg = round(float(avg_row[0]), 1)
            p_conn = product_db.connect()
            p_conn.execute(
                "UPDATE products SET rating = ? WHERE id = ?",
                (new_avg, product_id)
            )
            p_conn.commit()
            p_conn.close()

        conn.commit()

        # Trả về review mới kèm thông tin ảnh sản phẩm
        row = conn.execute(
            """
            SELECT id, username, rating, comment, created_at
            FROM reviews
            WHERE product_id = ? AND username = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (product_id, username)
        ).fetchone()
        conn.close()

        product = get_product_by_id(product_db, product_id)
        review = {
            "id": row["id"],
            "username": row["username"],
            "rating": row["rating"],
            "comment": row["comment"],
            "createdAt": row["created_at"],
            "productImage": product["image"] if product else "",
        }
        return jsonify({"success": True, "message": "Đã gửi bình luận!", "review": review})
    except Exception as e:
        conn.close()
        if "UNIQUE constraint failed" in str(e):
            return jsonify({"success": False, "message": "Bạn đã bình luận sản phẩm này rồi!"}), 400
        return jsonify({"success": False, "message": "Lỗi khi gửi bình luận!"}), 500


def check_is_admin(username):
    conn = customer_db.connect()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    # OOP: Đa hình - Khởi tạo đúng loại object
    user = User.from_db_row(dict(row) if row else None)
    if not user:
        return False
        
    # OOP: Đa hình - Gọi hàm has_permission để kiểm tra quyền
    return user.has_permission("manage_products")

@app.route("/api/admin/products", methods=["POST"])
def api_admin_add_product():
    username = get_username_from_request()
    if not check_is_admin(username):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    
    # Lấy dữ liệu từ form-data hoặc JSON
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = request.form
        image_url = data.get("image", "")
        file = request.files.get("image_file")
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"success": False, "message": "Định dạng file không được hỗ trợ! Chỉ chấp nhận ảnh (png, jpg, jpeg, gif, webp)."}), 400
            
            import uuid
            safe_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{safe_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                image_url = f"http://localhost:5000/uploads/{filename}"
            except Exception as e:
                print(f"Lỗi khi lưu file ảnh: {e}")
                return jsonify({"success": False, "message": "Lưu file thất bại, file có thể bị hỏng. Vui lòng thử lại!"}), 400
    else:
        data = request.json or {}
        image_url = data.get("image", "")
        
    name = data.get("name", "")
    description = data.get("description", "")
    
    # Dịch tự động bằng Google Translate
    name_en = ""
    description_en = ""
    try:
        translator = GoogleTranslator(source='auto', target='en')
        if name: name_en = translator.translate(name)
        if description: description_en = translator.translate(description)
    except Exception as e:
        print("Lỗi dịch:", e)
        
    conn = product_db.connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO products (name, name_en, description, description_en, price, original_price, stock, location, category_id, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                name_en,
                description,
                description_en,
                int(data.get("price", 0)),
                int(data.get("originalPrice", 0)),
                int(data.get("stock", 0)),
                data.get("location", ""),
                int(data.get("categoryId", 1)),
                image_url
            )
        )
        conn.commit()
        return jsonify({"success": True, "message": "Thêm sản phẩm thành công", "product_id": cur.lastrowid})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/admin/products/<int:product_id>", methods=["PUT"])
def api_admin_update_product(product_id):
    username = get_username_from_request()
    if not check_is_admin(username):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = request.form
        image_url = data.get("image", "")
        file = request.files.get("image_file")
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"success": False, "message": "Định dạng file không được hỗ trợ! Chỉ chấp nhận ảnh (png, jpg, jpeg, gif, webp)."}), 400
            
            import uuid
            safe_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{safe_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                image_url = f"http://localhost:5000/uploads/{filename}"
            except Exception as e:
                print(f"Lỗi khi lưu file ảnh: {e}")
                return jsonify({"success": False, "message": "Lưu file thất bại, file có thể bị hỏng. Vui lòng thử lại!"}), 400
    else:
        data = request.json or {}
        image_url = data.get("image", "")
        
    name = data.get("name", "")
    description = data.get("description", "")
    
    # Dịch tự động bằng Google Translate
    name_en = ""
    description_en = ""
    try:
        translator = GoogleTranslator(source='auto', target='en')
        if name: name_en = translator.translate(name)
        if description: description_en = translator.translate(description)
    except Exception as e:
        print("Lỗi dịch:", e)
        
    conn = product_db.connect()
    try:
        conn.execute(
            """
            UPDATE products
            SET name = ?, name_en = ?, description = ?, description_en = ?, price = ?, original_price = ?, stock = ?, location = ?, category_id = ?, image = ?, updated_at = datetime('now','localtime')
            WHERE id = ?
            """,
            (
                name,
                name_en,
                description,
                description_en,
                int(data.get("price", 0)),
                int(data.get("originalPrice", 0)),
                int(data.get("stock", 0)),
                data.get("location", ""),
                int(data.get("categoryId", 1)),
                image_url,
                product_id
            )
        )
        conn.commit()
        return jsonify({"success": True, "message": "Cập nhật sản phẩm thành công"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def api_admin_delete_product(product_id):
    username = get_username_from_request()
    if not check_is_admin(username):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    conn = product_db.connect()
    try:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Xóa sản phẩm thành công"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/admin/reviews/<int:review_id>", methods=["DELETE"])
def api_admin_delete_review(review_id):
    username = get_username_from_request()
    if not check_is_admin(username):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    conn = db.connect()
    try:
        conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Xóa bình luận thành công"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/admin/test-order", methods=["POST"])
def api_admin_test_order():
    username = get_username_from_request()
    if not check_is_admin(username):
        return jsonify({"success": False, "message": "Forbidden"}), 403
    
    data = request.json or {}
    buyer = data.get("buyer", "admin")
    total = int(data.get("total", 0))
    note = data.get("note", "Test Order")
    delivery_date = data.get("deliveryDate", "")
    
    conn = db.connect()
    try:
        cur = conn.execute(
            "INSERT INTO orders (username, total, status, note, delivery_date) VALUES (?, ?, ?, ?, ?)",
            (buyer, total, "pending", note, delivery_date)
        )
        order_id = cur.lastrowid
        conn.commit()
        return jsonify({"success": True, "message": "Tạo đơn hàng test thành công", "order_id": order_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
