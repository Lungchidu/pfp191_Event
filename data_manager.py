import csv
import os
from equipment import Equipment
from rental import Rental

EQUIPMENT_FILE = "equipment.csv"
RENTAL_FILE = "rental.csv"
USERS_FILE = "users.csv"

def load_equipment():
    # Tạo từ điển rỗng để chứa thiết bị
    equipment_dict = {}
    if not os.path.exists(EQUIPMENT_FILE):
        return equipment_dict

    try:
        with open(EQUIPMENT_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    eq = Equipment.from_dict(row)
                    equipment_dict[eq.equipment_id] = eq
                except Exception as e:
                    # Lấy equipment_id từ row, nếu không có thì để trống
                    if "equipment_id" in row:
                        eq_id = row["equipment_id"]
                    else:
                        eq_id = ""
                    print("Error loading equipment " + str(eq_id) + ": " + str(e))
    except Exception as e:
        print("Failed to read " + EQUIPMENT_FILE + ": " + str(e))

    return equipment_dict

def save_equipment(equipment_dict):
    try:
        with open(EQUIPMENT_FILE, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ["equipment_id", "name", "power_rating", "hourly_rental_rate", "current_status"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for eq in equipment_dict.values():
                writer.writerow(eq.to_dict())
    except Exception as e:
        print("Failed to save equipment: " + str(e))

def load_rentals():
    # Tạo danh sách rỗng để chứa các đơn thuê
    rentals = []
    if not os.path.exists(RENTAL_FILE):
        return rentals

    try:
        with open(RENTAL_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r = Rental.from_dict(row)
                    rentals.append(r)
                except Exception as e:
                    # Lấy rental_id từ row, nếu không có thì để trống
                    if "rental_id" in row:
                        r_id = row["rental_id"]
                    else:
                        r_id = ""
                    print("Error loading rental " + str(r_id) + ": " + str(e))
    except Exception as e:
        print("Failed to read " + RENTAL_FILE + ": " + str(e))

    return rentals

def save_rentals(rentals):
    try:
        with open(RENTAL_FILE, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ["rental_id", "client_name", "start_time", "expected_return_time", "equipment_ids", "status"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rentals:
                writer.writerow(r.to_dict())
    except Exception as e:
        print("Failed to save rentals: " + str(e))

def _load_users_from_file(filepath):
    """Helper to load users from a specific CSV file."""
    users = {}
    if not os.path.exists(filepath):
        return users
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    username = row["username"].strip()
                    if username:
                        # Kiểm tra từng trường, nếu không có thì dùng giá trị mặc định
                        if "password" in row:
                            password = row["password"]
                        else:
                            password = ""

                        if "role" in row:
                            role = row["role"]
                        else:
                            role = "user"

                        if "full_name" in row:
                            full_name = row["full_name"]
                        else:
                            full_name = ""

                        if "email" in row:
                            email = row["email"]
                        else:
                            email = ""

                        users[username] = {
                            "username": username,
                            "password": password,
                            "role": role,
                            "full_name": full_name,
                            "email": email
                        }
                except Exception as e:
                    # Lấy username từ row, nếu không có thì để trống
                    if "username" in row:
                        u_name = row["username"]
                    else:
                        u_name = ""
                    print("Error loading user " + str(u_name) + ": " + str(e))
    except Exception as e:
        print("Failed to read " + str(filepath) + ": " + str(e))
    return users

def load_users():
    """Load user accounts from CSV file. Also checks backup file. Returns dict keyed by username."""
    # Đọc người dùng từ file chính
    users = _load_users_from_file(USERS_FILE)

    # Tạo tên file sao lưu (backup) từ tên file chính
    # Ví dụ: "users.csv" -> "users_backup.csv"
    backup_file = USERS_FILE.replace(".csv", "_backup.csv")

    # Kiểm tra xem file sao lưu có tồn tại không
    # File sao lưu được tạo khi file chính bị khóa lúc lưu
    if os.path.exists(backup_file):
        # Đọc người dùng từ file sao lưu
        backup_users = _load_users_from_file(backup_file)

        # Gộp dữ liệu: file sao lưu được ưu tiên vì nó mới hơn
        for username in backup_users:
            user_data = backup_users[username]
            users[username] = user_data

        # Thử gộp lại vào file chính và xóa file sao lưu
        try:
            with open(USERS_FILE, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ["username", "password", "role", "full_name", "email"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for user in users.values():
                    writer.writerow(user)
            # Xóa file sao lưu sau khi đã gộp thành công
            os.remove(backup_file)
        except:
            pass  # Sẽ gộp lại lần sau nếu lần này thất bại

    return users

def save_users(users):
    """Save user accounts to CSV file."""
    import time

    # Số lần thử lưu tối đa (phòng trường hợp file bị khóa)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Thử lưu vào file chính
            with open(USERS_FILE, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ["username", "password", "role", "full_name", "email"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for user in users.values():
                    writer.writerow(user)
            return  # Lưu thành công, thoát hàm

        except PermissionError:
            # File bị khóa (ví dụ: đang được mở bởi chương trình khác)
            if attempt < max_retries - 1:
                # Chờ 0.5 giây rồi thử lại
                time.sleep(0.5)
            else:
                # Đã thử hết số lần cho phép, lưu vào file sao lưu thay thế
                alt_file = USERS_FILE.replace(".csv", "_backup.csv")
                try:
                    with open(alt_file, mode='w', newline='', encoding='utf-8') as f:
                        fieldnames = ["username", "password", "role", "full_name", "email"]
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for user in users.values():
                            writer.writerow(user)
                    print("Note: Saved to '" + alt_file + "' because '" + USERS_FILE + "' is locked.")
                except Exception as e2:
                    print("Failed to save users: " + str(e2))

        except Exception as e:
            print("Failed to save users: " + str(e))
            return
