from datetime import datetime

class Rental:
    def __init__(self, rental_id, client_name, start_time, expected_return_time, equipment_ids, status="Pending"):
        self._rental_id = rental_id

        if not client_name or not client_name.strip():
            raise ValueError("Client name cannot be empty")
        self._client_name = client_name

        # Validation for times
        fmt = "%Y-%m-%d"
        try:
            st = datetime.strptime(start_time, fmt)
            rt = datetime.strptime(expected_return_time, fmt)
            if rt <= st:
                raise ValueError("Expected return time must be after start time")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Invalid date format. Please use YYYY-MM-DD")
            raise e

        self._start_time = start_time
        self._expected_return_time = expected_return_time
        self._equipment_ids = equipment_ids

        # Kiểm tra trạng thái hợp lệ bằng vòng lặp
        valid_statuses = ["Pending", "Paid", "Completed", "Cancelled"]
        status_is_valid = False
        for valid_status in valid_statuses:
            if status == valid_status:
                status_is_valid = True
        if not status_is_valid:
            raise ValueError("Status must be 'Pending', 'Paid', 'Completed', or 'Cancelled'")
        self._status = status

    @property
    def rental_id(self):
        return self._rental_id

    @property
    def client_name(self):
        return self._client_name

    @property
    def start_time(self):
        return self._start_time

    @property
    def expected_return_time(self):
        return self._expected_return_time

    @property
    def equipment_ids(self):
        return self._equipment_ids

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        # Kiểm tra trạng thái hợp lệ bằng vòng lặp
        valid_statuses = ["Pending", "Paid", "Completed", "Cancelled"]
        value_is_valid = False
        for valid_status in valid_statuses:
            if value == valid_status:
                value_is_valid = True
        if not value_is_valid:
            raise ValueError("Status must be 'Pending', 'Paid', 'Completed', or 'Cancelled'")
        self._status = value

    def calculate_duration_days(self):
        fmt = "%Y-%m-%d"
        st = datetime.strptime(self.start_time, fmt)
        rt = datetime.strptime(self.expected_return_time, fmt)
        duration = rt - st
        # Trả về số ngày, tối thiểu là 0
        if duration.days > 0:
            return duration.days
        else:
            return 0

    def calculate_fees(self, equipment_dict):
        """Calculate fees based on equipment rented and duration."""
        total_rate = 0
        for eq_id in self.equipment_ids:
            if eq_id in equipment_dict:
                total_rate = total_rate + equipment_dict[eq_id].hourly_rental_rate

        duration_days = self.calculate_duration_days()
        return total_rate * duration_days * 24

    def to_dict(self):
        # Nối các equipment_id bằng dấu ";" thủ công
        equipment_str = ""
        for i in range(len(self.equipment_ids)):
            if i == 0:
                equipment_str = self.equipment_ids[i]
            else:
                equipment_str = equipment_str + ";" + self.equipment_ids[i]

        result = {
            "rental_id": self.rental_id,
            "client_name": self.client_name,
            "start_time": self.start_time,
            "expected_return_time": self.expected_return_time,
            "equipment_ids": equipment_str,
            "status": self.status
        }
        return result

    # Tạo đối tượng Rental từ dictionary
    @classmethod
    def from_dict(cls, data):
        rental_id = data["rental_id"]
        client_name = data["client_name"]
        start_time = data["start_time"]
        expected_return_time = data["expected_return_time"]

        # Tách chuỗi equipment_ids bằng if/else rõ ràng
        raw_equipment_ids = data["equipment_ids"]
        if raw_equipment_ids:
            equipment_ids = raw_equipment_ids.split(";")
        else:
            equipment_ids = []

        # Kiểm tra key "status" có tồn tại không
        if "status" in data:
            status = data["status"]
        else:
            status = "Pending"

        rental = cls(rental_id, client_name, start_time, expected_return_time, equipment_ids, status)
        return rental

    def __str__(self):
        # Nối các equipment_id bằng dấu ", " thủ công
        equipment_display = ""
        for i in range(len(self.equipment_ids)):
            if i == 0:
                equipment_display = self.equipment_ids[i]
            else:
                equipment_display = equipment_display + ", " + self.equipment_ids[i]

        result = "Rental ID: " + str(self.rental_id) + " | Client: " + str(self.client_name) + " | Start: " + str(self.start_time) + " | Return: " + str(self.expected_return_time) + " | Status: " + str(self.status) + " | Equipments: " + equipment_display
        return result
