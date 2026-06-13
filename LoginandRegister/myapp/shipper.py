"""
shipper.py  –  EventRent Shipper Tracking Module
=================================================
Module quản lý và theo dõi shipper giao hàng cho EventRent.

Bảng mới được thêm vào event_rental.db:
  • shippers     – hồ sơ shipper (tên, SĐT, phương tiện, trạng thái)
  • deliveries   – đơn giao hàng gắn với order_id
  • delivery_logs – lịch sử cập nhật trạng thái (timeline)
  • delivery_locations – vị trí GPS cập nhật theo thời gian thực

Luồng trạng thái delivery:
  assigned → picked_up → in_transit → delivered
                                    ↘ failed

Cách dùng độc lập:
  from shipper import ShipperDB
  sdb = ShipperDB()
  sdb.init_tables()
"""

import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE_DIR, "event_rental.db")

# ──────────────────────────────────────────────────────────────
# Trạng thái hợp lệ
# ──────────────────────────────────────────────────────────────
DELIVERY_STATUSES = [
    "assigned",    # Đã phân công shipper
    "picked_up",   # Đã lấy hàng từ kho
    "in_transit",  # Đang trên đường giao
    "delivered",   # Giao thành công
    "failed",      # Giao thất bại
]

SHIPPER_STATUSES = [
    "available",   # Sẵn sàng nhận đơn
    "busy",        # Đang giao hàng
    "offline",     # Không hoạt động
]

VEHICLE_TYPES = ["xe_may", "o_to", "xe_tai"]

STATUS_LABEL = {
    "assigned":   "Đã phân công",
    "picked_up":  "Đã lấy hàng",
    "in_transit": "Đang giao",
    "delivered":  "Đã giao",
    "failed":     "Giao thất bại",
    "available":  "Sẵn sàng",
    "busy":       "Đang bận",
    "offline":    "Ngoại tuyến",
}

# Bước kế tiếp hợp lệ từ mỗi trạng thái
NEXT_STATUSES = {
    "assigned":   ["picked_up", "failed"],
    "picked_up":  ["in_transit", "failed"],
    "in_transit": ["delivered", "failed"],
    "delivered":  [],
    "failed":     [],
}


# ──────────────────────────────────────────────────────────────
# ShipperDB
# ──────────────────────────────────────────────────────────────
class ShipperDB:
    """Toàn bộ thao tác DB liên quan đến shipper và giao hàng."""

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file

    # ── kết nối ──────────────────────────────────────────────
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ── khởi tạo bảng ────────────────────────────────────────
    def init_tables(self) -> None:
        conn = self.connect()
        try:
            # ── Hồ sơ shipper ─────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shippers (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name    TEXT    NOT NULL,
                    phone        TEXT    NOT NULL UNIQUE,
                    vehicle_type TEXT    NOT NULL DEFAULT 'xe_may',
                    license_plate TEXT   NOT NULL DEFAULT '',
                    status       TEXT    NOT NULL DEFAULT 'available',
                    avatar_url   TEXT    DEFAULT '',
                    note         TEXT    DEFAULT '',
                    created_at   TEXT    DEFAULT (datetime('now','localtime'))
                )
            """)

            # ── Đơn giao hàng ─────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deliveries (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id        INTEGER NOT NULL,
                    shipper_id      INTEGER,
                    status          TEXT    NOT NULL DEFAULT 'assigned',
                    pickup_address  TEXT    NOT NULL DEFAULT '',
                    delivery_address TEXT   NOT NULL DEFAULT '',
                    recipient_name  TEXT    NOT NULL DEFAULT '',
                    recipient_phone TEXT    NOT NULL DEFAULT '',
                    note            TEXT    DEFAULT '',
                    estimated_time  TEXT    DEFAULT '',
                    actual_time     TEXT    DEFAULT '',
                    created_at      TEXT    DEFAULT (datetime('now','localtime')),
                    updated_at      TEXT    DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (order_id)   REFERENCES orders(id)    ON DELETE CASCADE,
                    FOREIGN KEY (shipper_id) REFERENCES shippers(id)  ON DELETE SET NULL
                )
            """)

            # ── Lịch sử cập nhật trạng thái (timeline) ────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delivery_logs (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    delivery_id   INTEGER NOT NULL,
                    status        TEXT    NOT NULL,
                    message       TEXT    DEFAULT '',
                    updated_by    TEXT    DEFAULT 'system',
                    created_at    TEXT    DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE
                )
            """)

            # ── Vị trí GPS shipper theo thời gian ─────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS delivery_locations (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    delivery_id  INTEGER NOT NULL,
                    shipper_id   INTEGER NOT NULL,
                    latitude     REAL    NOT NULL,
                    longitude    REAL    NOT NULL,
                    recorded_at  TEXT    DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (delivery_id) REFERENCES deliveries(id)  ON DELETE CASCADE,
                    FOREIGN KEY (shipper_id)  REFERENCES shippers(id)    ON DELETE CASCADE
                )
            """)

            conn.commit()
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    # SHIPPER CRUD
    # ──────────────────────────────────────────────────────────
    def create_shipper(self, data: dict) -> dict:
        """Tạo shipper mới. Trả về dict shipper vừa tạo."""
        conn = self.connect()
        try:
            cur = conn.execute(
                """INSERT INTO shippers (full_name, phone, vehicle_type, license_plate, status, avatar_url, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["full_name"], data["phone"],
                    data.get("vehicle_type", "xe_may"),
                    data.get("license_plate", ""),
                    data.get("status", "available"),
                    data.get("avatar_url", ""),
                    data.get("note", ""),
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM shippers WHERE id=?", (cur.lastrowid,)).fetchone()
            return _row_to_shipper(row)
        finally:
            conn.close()

    def get_all_shippers(self, status: str = None) -> list:
        conn = self.connect()
        try:
            if status:
                rows = conn.execute(
                    "SELECT * FROM shippers WHERE status=? ORDER BY id", (status,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM shippers ORDER BY id").fetchall()
            return [_row_to_shipper(r) for r in rows]
        finally:
            conn.close()

    def get_shipper(self, shipper_id: int) -> dict | None:
        conn = self.connect()
        try:
            row = conn.execute("SELECT * FROM shippers WHERE id=?", (shipper_id,)).fetchone()
            return _row_to_shipper(row) if row else None
        finally:
            conn.close()

    def update_shipper(self, shipper_id: int, data: dict) -> dict | None:
        """Cập nhật thông tin shipper. Chỉ cập nhật các trường có trong data."""
        allowed = ["full_name", "phone", "vehicle_type", "license_plate", "status", "avatar_url", "note"]
        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            return self.get_shipper(shipper_id)

        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [shipper_id]
        conn = self.connect()
        try:
            conn.execute(f"UPDATE shippers SET {set_clause} WHERE id=?", values)
            conn.commit()
            row = conn.execute("SELECT * FROM shippers WHERE id=?", (shipper_id,)).fetchone()
            return _row_to_shipper(row) if row else None
        finally:
            conn.close()

    def delete_shipper(self, shipper_id: int) -> bool:
        conn = self.connect()
        try:
            cur = conn.execute("DELETE FROM shippers WHERE id=?", (shipper_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    # DELIVERY CRUD
    # ──────────────────────────────────────────────────────────
    def create_delivery(self, data: dict) -> dict:
        """Tạo đơn giao hàng và ghi log 'assigned' đầu tiên."""
        conn = self.connect()
        try:
            cur = conn.execute(
                """INSERT INTO deliveries
                   (order_id, shipper_id, status, pickup_address, delivery_address,
                    recipient_name, recipient_phone, note, estimated_time)
                   VALUES (?, ?, 'assigned', ?, ?, ?, ?, ?, ?)""",
                (
                    data["order_id"],
                    data.get("shipper_id"),
                    data.get("pickup_address", "Kho EventRent – 123 Nguyễn Trãi, HCM"),
                    data.get("delivery_address", ""),
                    data.get("recipient_name", ""),
                    data.get("recipient_phone", ""),
                    data.get("note", ""),
                    data.get("estimated_time", ""),
                ),
            )
            delivery_id = cur.lastrowid

            # Ghi log khởi tạo
            conn.execute(
                """INSERT INTO delivery_logs (delivery_id, status, message, updated_by)
                   VALUES (?, 'assigned', ?, ?)""",
                (delivery_id, "Đơn hàng đã được phân công cho shipper.", data.get("created_by", "system")),
            )

            # Cập nhật trạng thái shipper → busy
            if data.get("shipper_id"):
                conn.execute(
                    "UPDATE shippers SET status='busy' WHERE id=?", (data["shipper_id"],)
                )

            conn.commit()
            return self.get_delivery(delivery_id)
        finally:
            conn.close()

    def get_delivery(self, delivery_id: int) -> dict | None:
        conn = self.connect()
        try:
            row = conn.execute(
                """SELECT d.*, s.full_name as shipper_name, s.phone as shipper_phone,
                          s.vehicle_type, s.license_plate
                   FROM deliveries d
                   LEFT JOIN shippers s ON d.shipper_id = s.id
                   WHERE d.id=?""",
                (delivery_id,),
            ).fetchone()
            if not row:
                return None
            result = _row_to_delivery(row)
            result["logs"]     = self.get_delivery_logs(delivery_id)
            result["location"] = self.get_latest_location(delivery_id)
            return result
        finally:
            conn.close()

    def get_deliveries(self, filters: dict = None) -> list:
        """Lấy danh sách đơn với filter: status, shipper_id, order_id."""
        filters = filters or {}
        wheres, params = [], []

        if filters.get("status"):
            wheres.append("d.status=?")
            params.append(filters["status"])
        if filters.get("shipper_id"):
            wheres.append("d.shipper_id=?")
            params.append(filters["shipper_id"])
        if filters.get("order_id"):
            wheres.append("d.order_id=?")
            params.append(filters["order_id"])

        where_sql = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        conn = self.connect()
        try:
            rows = conn.execute(
                f"""SELECT d.*, s.full_name as shipper_name, s.phone as shipper_phone,
                           s.vehicle_type, s.license_plate
                    FROM deliveries d
                    LEFT JOIN shippers s ON d.shipper_id = s.id
                    {where_sql}
                    ORDER BY d.created_at DESC""",
                params,
            ).fetchall()
            return [_row_to_delivery(r) for r in rows]
        finally:
            conn.close()

    def update_delivery_status(
        self, delivery_id: int, new_status: str, message: str = "", updated_by: str = "system"
    ) -> tuple[dict | None, str]:
        """
        Cập nhật trạng thái delivery.
        Trả về (delivery_dict, error_message).
        error_message là chuỗi rỗng nếu thành công.
        """
        if new_status not in DELIVERY_STATUSES:
            return None, f"Trạng thái '{new_status}' không hợp lệ."

        delivery = self.get_delivery(delivery_id)
        if not delivery:
            return None, "Không tìm thấy đơn giao hàng."

        current = delivery["status"]
        if new_status not in NEXT_STATUSES.get(current, []):
            allowed = NEXT_STATUSES.get(current, [])
            return None, (
                f"Không thể chuyển từ '{STATUS_LABEL.get(current)}' "
                f"sang '{STATUS_LABEL.get(new_status)}'. "
                f"Bước hợp lệ tiếp theo: {', '.join(STATUS_LABEL.get(s, s) for s in allowed) or 'Không có'}."
            )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self.connect()
        try:
            actual_time = now if new_status == "delivered" else ""
            conn.execute(
                """UPDATE deliveries SET status=?, updated_at=?, actual_time=CASE WHEN ?!='' THEN ? ELSE actual_time END
                   WHERE id=?""",
                (new_status, now, actual_time, actual_time, delivery_id),
            )

            # Ghi log
            default_msg = {
                "picked_up":  "Shipper đã đến kho và lấy hàng.",
                "in_transit": "Đơn hàng đang trên đường giao đến khách.",
                "delivered":  "Giao hàng thành công! Khách đã nhận hàng.",
                "failed":     "Giao hàng thất bại. Hàng sẽ được hoàn lại kho.",
            }
            conn.execute(
                """INSERT INTO delivery_logs (delivery_id, status, message, updated_by)
                   VALUES (?, ?, ?, ?)""",
                (delivery_id, new_status, message or default_msg.get(new_status, ""), updated_by),
            )

            # Cập nhật shipper status
            if delivery.get("shipper_id") and new_status in ("delivered", "failed"):
                conn.execute(
                    "UPDATE shippers SET status='available' WHERE id=?",
                    (delivery["shipper_id"],),
                )

            conn.commit()
            return self.get_delivery(delivery_id), ""
        finally:
            conn.close()

    def assign_shipper(self, delivery_id: int, shipper_id: int, updated_by: str = "admin") -> tuple[dict | None, str]:
        """Gán / thay đổi shipper cho đơn giao hàng."""
        shipper = self.get_shipper(shipper_id)
        if not shipper:
            return None, "Không tìm thấy shipper."
        if shipper["status"] == "offline":
            return None, "Shipper đang ngoại tuyến, không thể phân công."

        conn = self.connect()
        try:
            delivery = self.get_delivery(delivery_id)
            if not delivery:
                conn.close()
                return None, "Không tìm thấy đơn giao hàng."
            if delivery["status"] in ("delivered", "failed"):
                conn.close()
                return None, "Đơn hàng đã kết thúc, không thể thay đổi shipper."

            # Trả shipper cũ về available nếu có
            if delivery.get("shipper_id") and delivery["shipper_id"] != shipper_id:
                conn.execute(
                    "UPDATE shippers SET status='available' WHERE id=?",
                    (delivery["shipper_id"],),
                )

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "UPDATE deliveries SET shipper_id=?, updated_at=? WHERE id=?",
                (shipper_id, now, delivery_id),
            )
            conn.execute(
                "UPDATE shippers SET status='busy' WHERE id=?", (shipper_id,)
            )
            conn.execute(
                """INSERT INTO delivery_logs (delivery_id, status, message, updated_by)
                   VALUES (?, ?, ?, ?)""",
                (
                    delivery_id, delivery["status"],
                    f"Phân công lại cho shipper: {shipper['full_name']} ({shipper['phone']}).",
                    updated_by,
                ),
            )
            conn.commit()
            return self.get_delivery(delivery_id), ""
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    # LOGS & LOCATION
    # ──────────────────────────────────────────────────────────
    def get_delivery_logs(self, delivery_id: int) -> list:
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT * FROM delivery_logs WHERE delivery_id=? ORDER BY created_at ASC",
                (delivery_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_location(self, delivery_id: int, shipper_id: int, lat: float, lng: float) -> dict:
        """Ghi vị trí GPS mới nhất của shipper."""
        conn = self.connect()
        try:
            conn.execute(
                """INSERT INTO delivery_locations (delivery_id, shipper_id, latitude, longitude)
                   VALUES (?, ?, ?, ?)""",
                (delivery_id, shipper_id, lat, lng),
            )
            conn.commit()
            return {"delivery_id": delivery_id, "latitude": lat, "longitude": lng,
                    "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        finally:
            conn.close()

    def get_latest_location(self, delivery_id: int) -> dict | None:
        conn = self.connect()
        try:
            row = conn.execute(
                """SELECT * FROM delivery_locations WHERE delivery_id=?
                   ORDER BY recorded_at DESC LIMIT 1""",
                (delivery_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_location_history(self, delivery_id: int) -> list:
        conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT * FROM delivery_locations WHERE delivery_id=? ORDER BY recorded_at ASC",
                (delivery_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    # THỐNG KÊ
    # ──────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        conn = self.connect()
        try:
            total_d   = conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM deliveries GROUP BY status"
            ).fetchall()
            total_s   = conn.execute("SELECT COUNT(*) FROM shippers").fetchone()[0]
            by_s_status = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM shippers GROUP BY status"
            ).fetchall()

            delivery_counts = {r["status"]: r["cnt"] for r in by_status}
            shipper_counts  = {r["status"]: r["cnt"] for r in by_s_status}

            return {
                "totalDeliveries":  total_d,
                "deliveryByStatus": delivery_counts,
                "totalShippers":    total_s,
                "shipperByStatus":  shipper_counts,
            }
        finally:
            conn.close()


# ──────────────────────────────────────────────────────────────
# Helper: Row → dict
# ──────────────────────────────────────────────────────────────
def _row_to_shipper(row: sqlite3.Row) -> dict:
    return {
        "id":           row["id"],
        "fullName":     row["full_name"],
        "phone":        row["phone"],
        "vehicleType":  row["vehicle_type"],
        "licensePlate": row["license_plate"],
        "status":       row["status"],
        "statusLabel":  STATUS_LABEL.get(row["status"], row["status"]),
        "avatarUrl":    row["avatar_url"],
        "note":         row["note"],
        "createdAt":    row["created_at"],
    }


def _row_to_delivery(row: sqlite3.Row) -> dict:
    keys = row.keys()
    return {
        "id":              row["id"],
        "orderId":         row["order_id"],
        "shipperId":       row["shipper_id"],
        "shipperName":     row["shipper_name"]     if "shipper_name"     in keys else None,
        "shipperPhone":    row["shipper_phone"]    if "shipper_phone"    in keys else None,
        "vehicleType":     row["vehicle_type"]     if "vehicle_type"     in keys else None,
        "licensePlate":    row["license_plate"]    if "license_plate"    in keys else None,
        "status":          row["status"],
        "statusLabel":     STATUS_LABEL.get(row["status"], row["status"]),
        "nextStatuses":    NEXT_STATUSES.get(row["status"], []),
        "pickupAddress":   row["pickup_address"],
        "deliveryAddress": row["delivery_address"],
        "recipientName":   row["recipient_name"],
        "recipientPhone":  row["recipient_phone"],
        "note":            row["note"],
        "estimatedTime":   row["estimated_time"],
        "actualTime":      row["actual_time"],
        "createdAt":       row["created_at"],
        "updatedAt":       row["updated_at"],
    }

