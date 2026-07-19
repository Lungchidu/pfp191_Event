class Equipment:
    """
    1. Tính Đóng gói (Encapsulation):
    Che giấu các thuộc tính bằng dấu gạch dưới (VD: self._name) 
    và dùng các hàm @property (getter/setter) để kiểm soát việc đọc/ghi.
    """
    def __init__(self, equipment_id, name, power_rating, hourly_rental_rate, current_status="Available"):
        self._equipment_id = equipment_id
        self._name = name
        self._power_rating = float(power_rating)
        self._hourly_rental_rate = float(hourly_rental_rate)
        self._current_status = current_status

    # Getters
    @property
    def equipment_id(self):
        return self._equipment_id

    @property
    def name(self):
        return self._name

    @property
    def power_rating(self):
        return self._power_rating

    @property
    def hourly_rental_rate(self):
        return self._hourly_rental_rate

    @property
    def current_status(self):
        return self._current_status

    # Setters
    @name.setter
    def name(self, value):
        self._name = str(value)

    @power_rating.setter
    def power_rating(self, value):
        self._power_rating = float(value)

    @hourly_rental_rate.setter
    def hourly_rental_rate(self, value):
        self._hourly_rental_rate = float(value)

    @current_status.setter
    def current_status(self, value):
        self._current_status = value

    """
    2. Tính Trừu tượng (Abstraction):
    Hàm get_type_info() không chứa code thực thi ở lớp cha. Nó bắt buộc
    bất kỳ lớp con nào cũng phải tự viết lại hàm này, nếu không sẽ bị lỗi.
    """
    def get_type_info(self):
        raise NotImplementedError("Subclasses must implement get_type_info()")

    def to_dict(self):
        return {
            "equipment_id": self._equipment_id,
            "name": self._name,
            "power_rating": str(self._power_rating),
            "hourly_rental_rate": str(self._hourly_rental_rate),
            "current_status": self._current_status,
            "category": self.get_type_info()
        }

    """
    4. Tính Đa hình (Polymorphism):
    Hàm __str__ dùng hàm get_type_info(). Tùy thuộc vào việc đối tượng là 
    Audio hay Lighting, hàm này sẽ trả ra kết quả khác nhau.
    """
    def __str__(self):
        info = "[" + self.get_type_info() + "] "
        info = info + "ID: " + self._equipment_id + " | "
        info = info + "Name: " + self._name + " | "
        info = info + "Power: " + str(self._power_rating) + "W | "
        info = info + "Rate: $" + str(self._hourly_rental_rate) + "/h | "
        info = info + "Status: " + self._current_status
        return info


"""
3. Tính Kế thừa (Inheritance):
Các lớp AudioEquipment, LightingEquipment, GeneralEquipment kế thừa 
toàn bộ thuộc tính và phương thức từ lớp cha Equipment.
"""
class AudioEquipment(Equipment):
    def get_type_info(self):
        return "Audio"


class LightingEquipment(Equipment):
    def get_type_info(self):
        return "Lighting"


class GeneralEquipment(Equipment):
    def get_type_info(self):
        return "General"
