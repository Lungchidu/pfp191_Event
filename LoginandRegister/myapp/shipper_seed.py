"""
shipper_seed.py  –  Seed dữ liệu shipper và đơn giao hàng mẫu
==============================================================
Chạy độc lập:  python shipper_seed.py
                python shipper_seed.py --force   # seed lại từ đầu

Dữ liệu mẫu:
  • 6 shipper với phương tiện đa dạng
  • 5 đơn giao hàng ở các trạng thái khác nhau
  • Lịch sử log đầy đủ cho mỗi đơn
  • Vị trí GPS demo cho đơn đang giao
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shipper import ShipperDB

# ──────────────────────────────────────────────────────────────
# Dữ liệu shipper mẫu
# ──────────────────────────────────────────────────────────────
DEMO_SHIPPERS = [
    {
        "full_name":    "Nguyễn Văn An",
        "phone":        "0901111001",
        "vehicle_type": "xe_may",
        "license_plate": "59B1-12345",
        "status":       "busy",
        "note":         "Shipper kỳ cựu, 3 năm kinh nghiệm",
    },
    {
        "full_name":    "Trần Thị Bình",
        "phone":        "0902222002",
        "vehicle_type": "xe_may",
        "license_plate": "51F3-67890",
        "status":       "available",
        "note":         "",
    },
    {
        "full_name":    "Lê Hoàng Cường",
        "phone":        "0903333003",
        "vehicle_type": "o_to",
        "license_plate": "51H-99988",
        "status":       "busy",
        "note":         "Chuyên giao thiết bị lớn, nhà bạt, sân khấu",
    },
    {
        "full_name":    "Phạm Minh Đức",
        "phone":        "0904444004",
        "vehicle_type": "xe_tai",
        "license_plate": "51C-45678",
        "status":       "available",
        "note":         "Xe tải 1.5 tấn, giao combo concert",
    },
    {
        "full_name":    "Võ Thị Em",
        "phone":        "0905555005",
        "vehicle_type": "xe_may",
        "license_plate": "59P2-11223",
        "status":       "offline",
        "note":         "Nghỉ phép đến 10/06",
    },
    {
        "full_name":    "Đỗ Quốc Phong",
        "phone":        "0906666006",
        "vehicle_type": "o_to",
        "license_plate": "51K-33456",
        "status":       "available",
        "note":         "",
    },
]

# ──────────────────────────────────────────────────────────────
# Dữ liệu đơn giao hàng mẫu
# Shipper index trong DEMO_SHIPPERS (0-based)
# ──────────────────────────────────────────────────────────────
DEMO_DELIVERIES = [
    # Đơn 1 – đang giao (in_transit)
    {
        "order_id":        1,
        "shipper_idx":     0,   # Nguyễn Văn An
        "delivery_address": "123 Lê Văn Sỹ, Phường 13, Quận 3, HCM",
        "recipient_name":  "Chị Hương",
        "recipient_phone": "0987654321",
        "estimated_time":  "2026-06-06 16:00",
        "note":            "Gọi trước 30 phút",
        "final_status":    "in_transit",
        "gps":             (10.7769, 106.7009),   # HCM nội thành
    },
    # Đơn 2 – đã giao thành công
    {
        "order_id":        2,
        "shipper_idx":     2,   # Lê Hoàng Cường
        "delivery_address": "456 Nguyễn Huệ, Quận 1, HCM",
        "recipient_name":  "Anh Tuấn",
        "recipient_phone": "0912345678",
        "estimated_time":  "2026-06-05 14:00",
        "note":            "",
        "final_status":    "delivered",
        "gps":             None,
    },
    # Đơn 3 – mới phân công (assigned)
    {
        "order_id":        3,
        "shipper_idx":     1,   # Trần Thị Bình
        "delivery_address": "789 Đinh Tiên Hoàng, Bình Thạnh, HCM",
        "recipient_name":  "Chị Lan",
        "recipient_phone": "0971122334",
        "estimated_time":  "2026-06-07 09:00",
        "note":            "Tầng 4, tòa nhà Sunrise",
        "final_status":    "assigned",
        "gps":             None,
    },
    # Đơn 4 – đã lấy hàng (picked_up)
    {
        "order_id":        4,
        "shipper_idx":     2,   # Lê Hoàng Cường
        "delivery_address": "55 Võ Văn Tần, Quận 3, HCM",
        "recipient_name":  "Anh Minh",
        "recipient_phone": "0933112233",
        "estimated_time":  "2026-06-06 18:30",
        "note":            "",
        "final_status":    "picked_up",
        "gps":             (10.7850, 106.6920),
    },
    # Đơn 5 – giao thất bại
    {
        "order_id":        5,
        "shipper_idx":     0,   # Nguyễn Văn An
        "delivery_address": "21 Trần Hưng Đạo, Quận 5, HCM",
        "recipient_name":  "Anh Phong",
        "recipient_phone": "0944556677",
        "estimated_time":  "2026-06-04 15:00",
        "note":            "",
        "final_status":    "failed",
        "gps":             None,
    },
]

# Lịch sử log tương ứng với từng trạng thái cuối
STATUS_LOG_CHAIN = {
    "assigned":   ["assigned"],
    "picked_up":  ["assigned", "picked_up"],
    "in_transit": ["assigned", "picked_up", "in_transit"],
    "delivered":  ["assigned", "picked_up", "in_transit", "delivered"],
    "failed":     ["assigned", "picked_up", "failed"],
}

LOG_MESSAGES = {
    "assigned":   "Đơn hàng đã được phân công cho shipper.",
    "picked_up":  "Shipper đã đến kho và lấy hàng thành công.",
    "in_transit": "Đơn hàng đang trên đường giao đến khách.",
    "delivered":  "Giao hàng thành công! Khách đã nhận hàng.",
    "failed":     "Giao hàng thất bại – khách không ở địa điểm giao hàng.",
}


# ──────────────────────────────────────────────────────────────
# Seed function
# ──────────────────────────────────────────────────────────────
def seed_shippers(sdb: ShipperDB, force: bool = False) -> None:
    # Kiểm tra đã seed chưa
    existing = sdb.get_all_shippers()
    if existing and not force:
        print(f"[shipper_seed] Đã có {len(existing)} shipper. Bỏ qua. (dùng --force để seed lại)")
        return

    if force:
        conn = sdb.connect()
        for tbl in ["delivery_locations", "delivery_logs", "deliveries", "shippers"]:
            conn.execute(f"DELETE FROM {tbl}")
        conn.commit()
        conn.close()
        print("[shipper_seed] Đã xóa dữ liệu shipper/delivery cũ.")

    # Tạo shippers
    created_shippers = []
    for s_data in DEMO_SHIPPERS:
        try:
            # Tạm thời set status available để create_delivery không lỗi
            tmp = dict(s_data)
            tmp["status"] = "available"
            shipper = sdb.create_shipper(tmp)
            created_shippers.append(shipper)
            print(f"  + Shipper: {shipper['fullName']} ({shipper['phone']})")
        except Exception as e:
            print(f"  ! Lỗi tạo shipper {s_data['full_name']}: {e}")
            created_shippers.append(None)

    print(f"[shipper_seed] Đã tạo {sum(1 for s in created_shippers if s)} shipper.")

    # Tạo deliveries
    conn = sdb.connect()
    for d_data in DEMO_DELIVERIES:
        idx = d_data["shipper_idx"]
        shipper = created_shippers[idx] if idx < len(created_shippers) else None
        if not shipper:
            print(f"  ! Bỏ qua delivery order_id={d_data['order_id']}: không có shipper")
            continue

        # Tạo delivery
        delivery = sdb.create_delivery({
            "order_id":        d_data["order_id"],
            "shipper_id":      shipper["id"],
            "delivery_address": d_data["delivery_address"],
            "recipient_name":  d_data["recipient_name"],
            "recipient_phone": d_data["recipient_phone"],
            "estimated_time":  d_data["estimated_time"],
            "note":            d_data["note"],
        })
        print(f"  + Delivery #{delivery['id']} (order {d_data['order_id']}) → {d_data['final_status']}")

        # Tạo chuỗi log đến trạng thái cuối
        chain = STATUS_LOG_CHAIN.get(d_data["final_status"], [])
        # Bỏ qua log "assigned" đầu tiên vì create_delivery đã tạo rồi
        for status in chain[1:]:
            sdb.update_delivery_status(
                delivery["id"], status,
                LOG_MESSAGES.get(status, ""),
                updated_by="seed"
            )

        # Thêm GPS nếu có
        if d_data.get("gps"):
            lat, lng = d_data["gps"]
            sdb.update_location(delivery["id"], shipper["id"], lat, lng)

    # Đồng bộ lại status shipper (busy / available) theo thực tế
    for idx, s_data in enumerate(DEMO_SHIPPERS):
        shipper = created_shippers[idx]
        if shipper:
            conn.execute(
                "UPDATE shippers SET status=? WHERE id=?",
                (s_data["status"], shipper["id"])
            )
    conn.commit()
    conn.close()

    print(f"[shipper_seed] ✅ Seed shipper hoàn tất!")


# ──────────────────────────────────────────────────────────────
# Chạy trực tiếp
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    from database import Database

    parser = argparse.ArgumentParser(description="EventRent shipper seeder")
    parser.add_argument("--force", action="store_true", help="Xóa và seed lại")
    args = parser.parse_args()

    # Đảm bảo bảng chính tồn tại trước
    main_db = Database()
    main_db.init_tables()

    sdb = ShipperDB()
    sdb.init_tables()
    seed_shippers(sdb, force=args.force)

