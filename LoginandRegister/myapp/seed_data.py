"""
seed_data.py  –  EventRent database seeder (nâng cấp)
=======================================================
Chạy độc lập:  python seed_data.py
Hoặc import:   from seed_data import seed_all

Thêm mới so với phiên bản cũ:
  • 20 sản phẩm (thêm 8 sản phẩm mới)
  • Tài khoản admin mặc định (admin / Admin@1234)
  • Tài khoản demo khách hàng (demo / Demo@1234)
  • Reviews mẫu
  • Wishlist mẫu
"""

import json
import os
import sys

import bcrypt

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cho phép chạy trực tiếp từ thư mục này
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database, CustomerDatabase, ProductDatabase

# ──────────────────────────────────────────────────────────────
# Dữ liệu mẫu
# ──────────────────────────────────────────────────────────────
CATEGORIES = [
    {"id": 1,  "name": "Âm thanh",         "icon": "volume"},
    {"id": 2,  "name": "Ánh sáng",          "icon": "lightbulb"},
    {"id": 3,  "name": "Sân khấu",          "icon": "stage"},
    {"id": 4,  "name": "Nhà bạt",           "icon": "tent"},
    {"id": 5,  "name": "Bàn ghế",           "icon": "chair"},
    {"id": 6,  "name": "Màn hình LED",      "icon": "monitor"},
    {"id": 7,  "name": "Máy chiếu",         "icon": "projector"},
    {"id": 8,  "name": "Micro & DJ",        "icon": "mic"},
    {"id": 9,  "name": "Generator",         "icon": "zap"},
    {"id": 10, "name": "Dây & Phụ kiện",    "icon": "cable"},
    {"id": 11, "name": "Trang trí",         "icon": "sparkles"},
    {"id": 12, "name": "Backline",          "icon": "guitar"},
    {"id": 13, "name": "Camera live",       "icon": "camera"},
    {"id": 14, "name": "Logistics",         "icon": "package"},
    {"id": 15, "name": "Nhân sự kỹ thuật", "icon": "users"},
    {"id": 16, "name": "Gói combo",         "icon": "boxes"},
]

PRODUCTS = [
    # ── Âm thanh ─────────────────────────────────────────────
    {
        "id": 1,
        "name": "Loa line array 12 inch",
        "description": "Hệ thống loa line array công suất cao, phù hợp sân khấu ngoài trời 500–2000 khách. Bao gồm amply và dây tín hiệu.",
        "price": 850_000,    "original_price": 1_200_000, "discount": 29,
        "sold": 72,  "stock": 100, "rating": 4.8,
        "location": "Hồ Chí Minh", "category_id": 1, "is_flash": 1,
        "tags":  ["loa", "âm thanh", "line array"],
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&q=80",
        "specs": ["Công suất 2000W", "Bluetooth/Dante", "Kèm stand"],
    },
    {
        "id": 7,
        "name": "Loa JBL EON 715",
        "description": "Loa active 15 inch, bluetooth, phù hợp hội thảo 50–300 người.",
        "price": 500_000,    "original_price": 650_000, "discount": 23,
        "sold": 88,  "stock": 120, "rating": 4.6,
        "location": "Hồ Chí Minh", "category_id": 1, "is_flash": 0,
        "tags":  ["loa", "JBL", "active"],
        "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80",
        "specs": ["15 inch", "1300W", "Bluetooth"],
    },
    {
        "id": 17,
        "name": "Subwoofer 18 inch kép",
        "description": "2 loa sub 18 inch chất lượng cao, bass rền cho đại nhạc hội.",
        "price": 700_000,    "original_price": 950_000, "discount": 26,
        "sold": 33,  "stock": 40, "rating": 4.7,
        "location": "Hà Nội", "category_id": 1, "is_flash": 0,
        "tags":  ["loa", "sub", "bass"],
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&q=80",
        "specs": ["2x18 inch", "4000W tổng", "Kèm cáp XLR"],
    },
    # ── Ánh sáng ─────────────────────────────────────────────
    {
        "id": 2,
        "name": "Đèn moving head beam 380",
        "description": "Đèn beam 380W, 16 màu, phù hợp club và sự kiện. Hỗ trợ DMX512.",
        "price": 420_000,    "original_price": 580_000, "discount": 28,
        "sold": 45,  "stock": 60, "rating": 4.7,
        "location": "Hà Nội", "category_id": 2, "is_flash": 1,
        "tags":  ["đèn", "beam", "ánh sáng"],
        "image": "https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?w=800&q=80",
        "specs": ["380W", "DMX512", "Góc beam 3°"],
    },
    {
        "id": 18,
        "name": "Đèn PAR LED 54x3W (bộ 8 cái)",
        "description": "Bộ 8 đèn PAR LED chiếu màu sân khấu, kèm controller DMX.",
        "price": 280_000,    "original_price": 380_000, "discount": 26,
        "sold": 61,  "stock": 80, "rating": 4.5,
        "location": "Hồ Chí Minh", "category_id": 2, "is_flash": 0,
        "tags":  ["đèn par", "LED", "sân khấu"],
        "image": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&q=80",
        "specs": ["54x3W/cái", "RGB", "Kèm DMX controller"],
    },
    # ── Sân khấu ─────────────────────────────────────────────
    {
        "id": 3,
        "name": "Sân khấu 6x4m gấp",
        "description": "Khung sân khấu nhôm gấp, mặt sàn gỗ chống trượt, cao 80cm.",
        "price": 2_100_000,  "original_price": 2_800_000, "discount": 25,
        "sold": 18,  "stock": 30, "rating": 4.9,
        "location": "Đà Nẵng", "category_id": 3, "is_flash": 1,
        "tags":  ["sân khấu", "lắp đặt"],
        "image": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800&q=80",
        "specs": ["6x4m", "Tải 500kg/m²", "Kèm lắp đặt"],
    },
    {
        "id": 19,
        "name": "Sân khấu T-shape 10x6m",
        "description": "Sân khấu hình chữ T cao cấp, phù hợp show thời trang và trình diễn.",
        "price": 4_500_000,  "original_price": 6_000_000, "discount": 25,
        "sold": 8,   "stock": 10, "rating": 5.0,
        "location": "Hồ Chí Minh", "category_id": 3, "is_flash": 0,
        "tags":  ["sân khấu", "T-shape", "thời trang"],
        "image": "https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&q=80",
        "specs": ["10x6m", "Tải 750kg/m²", "Kèm carpet đỏ"],
    },
    # ── Nhà bạt ──────────────────────────────────────────────
    {
        "id": 4,
        "name": "Nhà bạt 10x20m",
        "description": "Nhà bạt khung nhôm, mái PVC chống UV, có thể kết hợp AC.",
        "price": 3_500_000,  "original_price": 4_500_000, "discount": 22,
        "sold": 9,   "stock": 20, "rating": 4.6,
        "location": "Hồ Chí Minh", "category_id": 4, "is_flash": 1,
        "tags":  ["nhà bạt", "wedding", "ngoài trời"],
        "image": "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=800&q=80",
        "specs": ["10x20m", "Chống UV", "Kèm neo"],
    },
    # ── Bàn ghế ──────────────────────────────────────────────
    {
        "id": 8,
        "name": "Bàn tròn sự kiện + ghế",
        "description": "Combo 10 bàn tròn kèm 80 ghế banquet có phủ khăn.",
        "price": 150_000,    "original_price": 200_000, "discount": 25,
        "sold": 120, "stock": 200, "rating": 4.4,
        "location": "Đà Nẵng", "category_id": 5, "is_flash": 0,
        "tags":  ["bàn ghế", "wedding", "banquet"],
        "image": "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?w=800&q=80",
        "specs": ["10 bàn", "80 ghế", "Kèm phủ"],
    },
    # ── Màn hình LED ─────────────────────────────────────────
    {
        "id": 6,
        "name": "LED wall P3.9 indoor",
        "description": "Màn hình LED trong nhà P3.9 độ sáng cao, kèm processor.",
        "price": 5_200_000,  "original_price": 6_800_000, "discount": 24,
        "sold": 6,   "stock": 15, "rating": 4.9,
        "location": "Hồ Chí Minh", "category_id": 6, "is_flash": 1,
        "tags":  ["led", "màn hình", "indoor"],
        "image": "https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?w=800&q=80",
        "specs": ["P3.9", "Indoor", "Kèm processor"],
    },
    {
        "id": 20,
        "name": "LED wall P4.8 outdoor 6m²",
        "description": "Màn hình LED ngoài trời P4.8, chống thấm IP65, 6m² lắp đặt.",
        "price": 8_000_000,  "original_price": 10_500_000, "discount": 24,
        "sold": 4,   "stock": 8, "rating": 4.8,
        "location": "Hà Nội", "category_id": 6, "is_flash": 0,
        "tags":  ["led", "outdoor", "màn hình"],
        "image": "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=800&q=80",
        "specs": ["P4.8", "IP65", "6m²", "Kèm cấu trúc"],
    },
    # ── Máy chiếu ────────────────────────────────────────────
    {
        "id": 11,
        "name": "Máy chiếu 8000 lumens",
        "description": "Máy chiếu Full HD 8000lm, kèm màn 120 inch cho hội thảo.",
        "price": 600_000,    "original_price": 800_000, "discount": 25,
        "sold": 42,  "stock": 60, "rating": 4.5,
        "location": "Hà Nội", "category_id": 7, "is_flash": 0,
        "tags":  ["máy chiếu", "projector", "hội thảo"],
        "image": "https://images.unsplash.com/photo-1535016120720-40c646be5580?w=800&q=80",
        "specs": ["8000lm", "Full HD", "Màn 120 inch"],
    },
    # ── Micro & DJ ───────────────────────────────────────────
    {
        "id": 12,
        "name": "Bộ micro không dây Shure",
        "description": "2 micro cầm + 1 micro cài áo, receiver UHF chống nhiễu.",
        "price": 350_000,    "original_price": 450_000, "discount": 22,
        "sold": 67,  "stock": 90, "rating": 4.8,
        "location": "Hồ Chí Minh", "category_id": 8, "is_flash": 0,
        "tags":  ["micro", "shure", "không dây"],
        "image": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&q=80",
        "specs": ["UHF", "3 micro", "Pin 8h"],
    },
    # ── Generator ────────────────────────────────────────────
    {
        "id": 5,
        "name": "Máy phát điện 20KVA",
        "description": "Máy phát diesel 20KVA cách âm, phù hợp sự kiện ngoài trời.",
        "price": 1_800_000,  "original_price": 2_400_000, "discount": 25,
        "sold": 31,  "stock": 50, "rating": 4.5,
        "location": "Hà Nội", "category_id": 9, "is_flash": 1,
        "tags":  ["máy phát điện", "generator"],
        "image": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800&q=80",
        "specs": ["20KVA", "Diesel", "Ồn < 75dB"],
    },
    # ── Camera live ──────────────────────────────────────────
    {
        "id": 21,
        "name": "Gói camera livestream 4K (3 góc)",
        "description": "3 camera Sony 4K, bộ switch OBS, kỹ thuật viên 1 ngày.",
        "price": 3_200_000,  "original_price": 4_200_000, "discount": 24,
        "sold": 15,  "stock": 10, "rating": 4.9,
        "location": "Hồ Chí Minh", "category_id": 13, "is_flash": 0,
        "tags":  ["camera", "livestream", "4K"],
        "image": "https://images.unsplash.com/photo-1617802690992-15d93263d3a9?w=800&q=80",
        "specs": ["3x Sony 4K", "OBS switch", "Kỹ thuật viên"],
    },
    # ── Logistics ────────────────────────────────────────────
    {
        "id": 9,
        "name": "Gói logistics sự kiện 24h",
        "description": "Vận chuyển – lắp đặt – thu hồi trong 24h nội thành HCM.",
        "price": 800_000,    "original_price": 1_000_000, "discount": 20,
        "sold": 55,  "stock": 80, "rating": 4.7,
        "location": "Hồ Chí Minh", "category_id": 14, "is_flash": 0,
        "tags":  ["logistics", "giao hàng", "lắp đặt"],
        "image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80",
        "specs": ["24h", "Nội thành HCM", "Kèm bảo hiểm"],
    },
    # ── Nhân sự kỹ thuật ─────────────────────────────────────
    {
        "id": 22,
        "name": "Kỹ thuật viên âm thanh ngày sự kiện",
        "description": "KTV chuyên nghiệp mix live sound, kinh nghiệm concert.",
        "price": 1_200_000,  "original_price": 1_600_000, "discount": 25,
        "sold": 28,  "stock": 20, "rating": 5.0,
        "location": "Hồ Chí Minh", "category_id": 15, "is_flash": 0,
        "tags":  ["kỹ thuật viên", "sound engineer", "nhân sự"],
        "image": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
        "specs": ["1 ngày 8h", "Kinh nghiệm 5+ năm", "Kèm tư vấn"],
    },
    # ── Gói combo ────────────────────────────────────────────
    {
        "id": 10,
        "name": "Combo wedding âm thanh + ánh sáng",
        "description": "Trọn gói loa, đèn par, sương khói cho tiệc cưới 200 khách.",
        "price": 4_500_000,  "original_price": 6_000_000, "discount": 25,
        "sold": 34,  "stock": 40, "rating": 4.9,
        "location": "Hà Nội", "category_id": 16, "is_flash": 0,
        "tags":  ["combo", "wedding", "trọn gói"],
        "image": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&q=80",
        "specs": ["200 khách", "Kỹ thuật 2 người", "Rehearsal 1 buổi"],
    },
    {
        "id": 23,
        "name": "Combo hội nghị 100 khách",
        "description": "Màn chiếu + PA system + micro không dây + setup cho hội nghị.",
        "price": 2_800_000,  "original_price": 3_800_000, "discount": 26,
        "sold": 22,  "stock": 30, "rating": 4.8,
        "location": "Hà Nội", "category_id": 16, "is_flash": 1,
        "tags":  ["combo", "hội nghị", "corporate"],
        "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80",
        "specs": ["100 khách", "PA + màn 150 inch", "2 micro không dây"],
    },
    {
        "id": 24,
        "name": "Combo concert 500 – 1000 khách",
        "description": "Hệ thống line array, LED wall, lighting rig, backline đầy đủ.",
        "price": 25_000_000, "original_price": 32_000_000, "discount": 22,
        "sold": 5,   "stock": 5, "rating": 5.0,
        "location": "Hồ Chí Minh", "category_id": 16, "is_flash": 0,
        "tags":  ["combo", "concert", "festival"],
        "image": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80",
        "specs": ["500–1000 khách", "Full production", "Team 8 KTV"],
    },
    # ── Dây & Phụ kiện ───────────────────────────────────────
    {
        "id": 25,
        "name": "Cuộn dây cáp tín hiệu XLR 50m",
        "description": "Dây cáp tín hiệu âm thanh XLR chuyên dụng chống nhiễu, lõi đồng chất lượng cao.",
        "price": 150_000,    "original_price": 200_000, "discount": 25,
        "sold": 90,  "stock": 150, "rating": 4.8,
        "location": "Hà Nội", "category_id": 10, "is_flash": 0,
        "tags":  ["cáp tín hiệu", "phụ kiện", "dây xlr"],
        "image": "https://images.unsplash.com/photo-1516223725307-6f76b9ec8742?w=800&q=80",
        "specs": ["Chiều dài 50m", "Hãng Soundking", "Chống nhiễu tốt"],
    },
    # ── Trang trí ────────────────────────────────────────────
    {
        "id": 26,
        "name": "Gói hoa tươi trang trí lối đi sân khấu",
        "description": "Trang trí thảm đỏ và hoa tươi lối đi, thiết kế chuyên nghiệp theo tone màu chủ đạo của tiệc.",
        "price": 1_200_000,  "original_price": 1_600_000, "discount": 25,
        "sold": 40,  "stock": 50, "rating": 4.9,
        "location": "Đà Nẵng", "category_id": 11, "is_flash": 0,
        "tags":  ["trang trí", "hoa tươi", "wedding"],
        "image": "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?w=800&q=80",
        "specs": ["Hoa hồng/Cẩm tú cầu", "Kèm chân sắt nghệ thuật", "Thiết kế theo tone màu"],
    },
    # ── Backline ─────────────────────────────────────────────
    {
        "id": 27,
        "name": "Bộ trống Jazz Yamaha Stage Custom",
        "description": "Bộ trống Jazz cao cấp phục vụ biểu diễn live band, âm thanh uy lực chuẩn concert.",
        "price": 1_500_000,  "original_price": 2_000_000, "discount": 25,
        "sold": 12,  "stock": 15, "rating": 4.7,
        "location": "Hà Nội", "category_id": 12, "is_flash": 0,
        "tags":  ["trống", "backline", "nhạc cụ"],
        "image": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800&q=80",
        "specs": ["Trống cơ 5 pcs", "Kèm cymbals Zildjian", "Hardware đầy đủ"],
    },
]

# Dữ liệu demo accounts
DEMO_USERS = [
    {
        "username":  "admin",
        "password":  "Admin@1234",
        "email":     "admin@eventrent.vn",
        "full_name": "Quản trị viên",
        "phone":     "0900000001",
        "role":      "admin",
    },
    {
        "username":  "adc@bua.nhan",
        "password":  "quangbolahut",
        "email":     "adc@bua.nhan",
        "full_name": "Admin ADC",
        "phone":     "0900000003",
        "role":      "admin",
    },
    {
        "username":  "demo",
        "password":  "Demo@1234",
        "email":     "demo@eventrent.vn",
        "full_name": "Khách Demo",
        "phone":     "0900000002",
        "role":      "customer",
    },
]

DEMO_REVIEWS = [
    {"product_id": 1,  "username": "demo", "rating": 5, "comment": "Loa rất to và rõ, kỹ thuật viên nhiệt tình!"},
    {"product_id": 2,  "username": "demo", "rating": 4, "comment": "Đèn đẹp, setup hơi lâu nhưng kết quả ổn."},
    {"product_id": 10, "username": "demo", "rating": 5, "comment": "Combo wedding xuất sắc, ai cũng khen."},
]

DEMO_WISHLIST = [
    {"username": "demo", "product_id": 6},
    {"username": "demo", "product_id": 10},
    {"username": "demo", "product_id": 24},
]


# ──────────────────────────────────────────────────────────────
# Hàm seed chính
# ──────────────────────────────────────────────────────────────
def seed_all(db: Database, customer_db: CustomerDatabase, product_db: ProductDatabase = None, force: bool = False) -> None:
    """
    Seed toàn bộ dữ liệu mẫu.
    force=True: xóa dữ liệu cũ và seed lại từ đầu.
    
    - product_db: chứa categories + products
    - db:         chứa cart_items, orders, order_items, reviews, wishlist
    - customer_db: chứa users
    """
    if product_db is None:
        product_db = ProductDatabase()
        product_db.init_tables(create_if_missing=True)

    conn = db.connect(create_if_missing=True)
    customer_conn = customer_db.connect(create_if_missing=True)
    product_conn = product_db.connect(create_if_missing=True)

    try:
        existing_products = product_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if existing_products > 0 and not force:
            print(f"[seed] Da co {existing_products} san pham. Bo qua. (dung force=True de seed lai)")
            return

        if force:
            # Xóa dữ liệu cũ trong từng database
            for tbl in ["products", "categories"]:
                product_conn.execute(f"DELETE FROM {tbl}")
            for tbl in ["reviews", "wishlist", "order_items", "cart_items", "orders"]:
                try:
                    conn.execute(f"DELETE FROM {tbl}")
                except Exception:
                    pass
            customer_conn.execute("DELETE FROM users")
            print("[seed] Da xoa du lieu cu.")

        # ── Danh mục (vào products.db) ────────────────────────
        for cat in CATEGORIES:
            product_conn.execute(
                "INSERT OR IGNORE INTO categories (id, name, icon) VALUES (?, ?, ?)",
                (cat["id"], cat["name"], cat["icon"]),
            )
        print(f"[seed] Da them {len(CATEGORIES)} danh muc.")

        # ── Sản phẩm (vào products.db) ────────────────────────
        for p in PRODUCTS:
            product_conn.execute(
                """INSERT OR IGNORE INTO products
                   (id, name, description, price, original_price, discount,
                    sold, stock, rating, location, category_id, is_flash, tags, image, specs)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p["id"], p["name"], p["description"],
                    p["price"], p["original_price"], p["discount"],
                    p["sold"], p["stock"], p["rating"], p["location"],
                    p["category_id"], p["is_flash"],
                    json.dumps(p["tags"],  ensure_ascii=False),
                    p["image"],
                    json.dumps(p["specs"], ensure_ascii=False),
                ),
            )
        print(f"[seed] Da them {len(PRODUCTS)} san pham.")

        # ── Tài khoản demo (vào customers.db) ─────────────────
        for u in DEMO_USERS:
            hashed = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()
            customer_conn.execute(
                """INSERT OR IGNORE INTO users
                   (username, password, email, full_name, phone, role)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (u["username"], hashed, u["email"], u["full_name"], u["phone"], u["role"]),
            )
        print(f"[seed] Da them {len(DEMO_USERS)} tai khoan demo.")

        # ── Reviews (vào event_rental.db) ─────────────────────
        for r in DEMO_REVIEWS:
            conn.execute(
                """INSERT OR IGNORE INTO reviews (product_id, username, rating, comment)
                   VALUES (?, ?, ?, ?)""",
                (r["product_id"], r["username"], r["rating"], r["comment"]),
            )
        print(f"[seed] Da them {len(DEMO_REVIEWS)} danh gia.")

        # ── Wishlist (vào event_rental.db) ─────────────────────
        for w in DEMO_WISHLIST:
            conn.execute(
                "INSERT OR IGNORE INTO wishlist (username, product_id) VALUES (?, ?)",
                (w["username"], w["product_id"]),
            )
        print(f"[seed] Da them {len(DEMO_WISHLIST)} wishlist items.")

        product_conn.commit()
        conn.commit()
        customer_conn.commit()
        print("[seed] Seed hoan tat!")

    finally:
        product_conn.close()
        conn.close()
        customer_conn.close()


# ──────────────────────────────────────────────────────────────
# Chạy trực tiếp
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EventRent database seeder")
    parser.add_argument("--force", action="store_true", help="Xoa va seed lai tu dau")
    args = parser.parse_args()

    product_db = ProductDatabase()
    product_db.init_tables(create_if_missing=True)
    db = Database()
    db.init_tables(create_if_missing=True)
    customer_db = CustomerDatabase()
    customer_db.init_tables(create_if_missing=True)
    seed_all(db, customer_db, product_db=product_db, force=args.force)

