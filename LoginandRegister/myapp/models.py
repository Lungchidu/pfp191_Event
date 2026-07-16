"""
models.py  –  EventRent User Models (OOP)
==========================================
Hệ thống phân quyền người dùng theo mô hình OOP đầy đủ 4 trụ cột:

  1. Đóng gói (Encapsulation):
     - Thuộc tính `_password` là private, chỉ truy cập qua check_password() / set_password()
     - Không bao giờ lộ password hash ra bên ngoài

  2. Trừu tượng (Abstraction):
     - Cung cấp interface đơn giản: login(), to_dict(), get_permissions()
     - Ẩn chi tiết xử lý bcrypt, truy vấn DB bên trong

  3. Kế thừa (Inheritance):
     - Customer(User) và Admin(User) kế thừa từ lớp cha User
     - Tái sử dụng toàn bộ thuộc tính và phương thức cơ bản

  4. Đa hình (Polymorphism):
     - Admin override get_permissions() để mở rộng quyền
     - Admin override to_dict() để thêm admin_level
     - Gọi user.get_permissions() hoạt động khác nhau tùy loại đối tượng

Cách dùng:
  from models import User, Customer, Admin

  # Tạo từ DB row
  user = User.from_db_row(row, customer_db)
  if user.has_permission("manage_products"):
      ...
"""

import bcrypt


# ──────────────────────────────────────────────────────────────
# Lớp cha: User
# ──────────────────────────────────────────────────────────────
class User:
    """Lớp cơ sở đại diện cho mọi người dùng trong hệ thống EventRent.

    Đóng gói (Encapsulation):
        - `_password` là thuộc tính protected, không truy cập trực tiếp từ bên ngoài.
        - Chỉ tương tác qua check_password() và set_password().

    Trừu tượng (Abstraction):
        - Cung cấp các method đơn giản: to_dict(), get_permissions(), has_permission()
        - Ẩn đi logic xử lý bcrypt hash/verify bên trong.
    """

    def __init__(self, username, email="", password_hash="",
                 full_name="", phone="", birth_year=0, address="",
                 role="customer", is_active=True, created_at=""):
        self.username = username
        self.email = email
        self._password = password_hash    # ← Đóng gói: thuộc tính protected
        self.full_name = full_name
        self.phone = phone
        self.birth_year = birth_year
        self.address = address
        self.role = role
        self.is_active = is_active
        self.created_at = created_at

    # ── Đóng gói: Kiểm tra mật khẩu (không lộ hash) ──────────
    def check_password(self, raw_password: str) -> bool:
        """Kiểm tra mật khẩu người dùng nhập vào có khớp với hash đã lưu không.
        Đóng gói: bảo vệ _password, chỉ cho phép kiểm tra đúng/sai."""
        if not self._password:
            return False
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self._password.encode("utf-8")
        )

    def set_password(self, new_password: str) -> None:
        """Hash và cập nhật mật khẩu mới.
        Đóng gói: không cho phép gán trực tiếp _password từ bên ngoài."""
        self._password = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    # ── Trừu tượng: Interface đơn giản cho bên ngoài ─────────
    def get_permissions(self) -> list:
        """Trả về danh sách quyền của người dùng.
        Đa hình: class con (Admin) sẽ override method này để mở rộng quyền."""
        return [
            "view_products",
            "add_to_cart",
            "checkout",
            "view_own_orders",
            "post_review",
        ]

    def has_permission(self, permission: str) -> bool:
        """Kiểm tra người dùng có quyền cụ thể hay không.
        Trừu tượng: gọi get_permissions() — kết quả phụ thuộc vào loại đối tượng (đa hình)."""
        return permission in self.get_permissions()

    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary (dùng cho JSON response).
        Đóng gói: KHÔNG bao gồm _password trong kết quả trả về.
        Đa hình: class con (Admin) sẽ override để thêm trường riêng."""
        return {
            "username":  self.username,
            "email":     self.email,
            "fullName":  self.full_name,
            "phone":     self.phone,
            "birthYear": self.birth_year,
            "address":    self.address,
            "role":      self.role,
            "isActive":  self.is_active,
            "createdAt": self.created_at,
            "permissions": self.get_permissions(),
        }

    def login(self, raw_password: str) -> bool:
        """Xác thực đăng nhập.
        Trừu tượng: ẩn đi logic kiểm tra mật khẩu bcrypt phức tạp bên trong."""
        if not self.is_active:
            return False
        return self.check_password(raw_password)

    # ── Factory method: Tạo đối tượng đúng loại từ DB row ────
    @staticmethod
    def from_db_row(row):
        """Tạo đối tượng User hoặc Admin từ kết quả truy vấn database.
        Đa hình: tự động trả về đúng loại class dựa trên trường 'role'."""
        if row is None:
            return None

        role = row["role"] if "role" in row.keys() else "customer"
        username = row["username"]
        password_hash = row["password"] if "password" in row.keys() else ""
        email = row["email"] if "email" in row.keys() else ""
        full_name = row["full_name"] if "full_name" in row.keys() else ""
        phone = row["phone"] if "phone" in row.keys() else ""
        birth_year = row["birth_year"] if "birth_year" in row.keys() else 0
        address = row["address"] if "address" in row.keys() else ""
        is_active = bool(row["is_active"]) if "is_active" in row.keys() else True
        created_at = row["created_at"] if "created_at" in row.keys() else ""

        if role == "admin":
            return Admin(
                username=username, email=email,
                password_hash=password_hash, full_name=full_name,
                phone=phone, birth_year=birth_year, address=address,
                is_active=is_active, created_at=created_at,
            )
        else:
            return Customer(
                username=username, email=email,
                password_hash=password_hash, full_name=full_name,
                phone=phone, birth_year=birth_year, address=address,
                is_active=is_active, created_at=created_at,
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} username='{self.username}' role='{self.role}'>"


# ──────────────────────────────────────────────────────────────
# Lớp con: Customer — Kế thừa hoàn toàn từ User
# ──────────────────────────────────────────────────────────────
class Customer(User):
    """Khách hàng bình thường — kế thừa toàn bộ từ User.

    Kế thừa (Inheritance):
        - Tái sử dụng 100% thuộc tính và method từ User.
        - Không cần viết lại bất kỳ logic nào.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("role", "customer")
        super().__init__(**kwargs)


# ──────────────────────────────────────────────────────────────
# Lớp con: Admin — Kế thừa + Mở rộng quyền
# ──────────────────────────────────────────────────────────────
class Admin(User):
    """Quản trị viên — kế thừa từ User, mở rộng quyền quản lý.

    Kế thừa (Inheritance):
        - Tái sử dụng thuộc tính và method cơ bản từ User (login, check_password, ...).

    Đa hình (Polymorphism):
        - Override get_permissions() → thêm quyền quản lý sản phẩm, đơn hàng, người dùng.
        - Override to_dict() → thêm trường admin_level vào kết quả.
        - Khi gọi user.get_permissions(), kết quả khác nhau tùy vào user là User hay Admin.
    """

    # Danh sách quyền đặc biệt chỉ dành cho Admin
    ADMIN_PERMISSIONS = [
        "manage_products",     # Thêm / sửa / xóa sản phẩm
        "manage_orders",       # Quản lý đơn hàng
        "view_all_orders",     # Xem tất cả đơn hàng (không chỉ của mình)
        "manage_users",        # Quản lý tài khoản người dùng
        "manage_reviews",      # Xóa bình luận
    ]

    def __init__(self, admin_level=1, **kwargs):
        kwargs.setdefault("role", "admin")
        super().__init__(**kwargs)            # ← Kế thừa: gọi __init__ của User
        self.admin_level = admin_level        # ← Thuộc tính riêng của Admin

    # ── Đa hình: Override get_permissions() ───────────────────
    def get_permissions(self) -> list:
        """Mở rộng quyền: bao gồm quyền cơ bản của User + quyền Admin.
        Đa hình: cùng tên method nhưng hành vi khác so với User.get_permissions()."""
        base_perms = super().get_permissions()    # ← Tái sử dụng từ lớp cha
        return base_perms + self.ADMIN_PERMISSIONS

    # ── Đa hình: Override to_dict() ───────────────────────────
    def to_dict(self) -> dict:
        """Mở rộng dict: thêm admin_level vào kết quả.
        Đa hình: cùng tên method nhưng trả về nhiều thông tin hơn User.to_dict()."""
        data = super().to_dict()                  # ← Tái sử dụng từ lớp cha
        data["adminLevel"] = self.admin_level
        return data

    # ── Quyền đặc biệt: Quản lý sản phẩm ─────────────────────
    def add_product(self, product_db, product_data: dict) -> dict:
        """Thêm sản phẩm mới vào database.
        Chỉ Admin mới có method này — Customer không có."""
        conn = product_db.connect()
        try:
            cur = conn.execute(
                """INSERT INTO products (name, description, price, original_price, stock, location, category_id, image)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    product_data.get("name", ""),
                    product_data.get("description", ""),
                    int(product_data.get("price", 0)),
                    int(product_data.get("originalPrice", 0)),
                    int(product_data.get("stock", 0)),
                    product_data.get("location", ""),
                    int(product_data.get("categoryId", 1)),
                    product_data.get("image", ""),
                )
            )
            conn.commit()
            return {"success": True, "product_id": cur.lastrowid}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def remove_product(self, product_db, product_id: int) -> dict:
        """Xóa sản phẩm khỏi database.
        Chỉ Admin mới có method này — Customer không có."""
        conn = product_db.connect()
        try:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return {"success": True}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def view_all_orders(self, order_db) -> list:
        """Xem toàn bộ đơn hàng trên hệ thống (không giới hạn theo username).
        Chỉ Admin mới có method này — Customer chỉ xem được đơn của mình."""
        conn = order_db.connect()
        try:
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY id DESC"
            ).fetchall()
            return [
                {
                    "id":        row["id"],
                    "username":  row["username"],
                    "total":     row["total"],
                    "status":    row["status"],
                    "note":      row["note"],
                    "createdAt": row["created_at"],
                }
                for row in rows
            ]
        finally:
            conn.close()
