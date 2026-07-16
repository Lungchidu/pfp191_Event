class Equipment:
    def __init__(self, equipment_id: str, name: str, power_rating: float, hourly_rental_rate: float, current_status: str = "Available"):
        self._equipment_id = equipment_id
        self._name = name
        self._power_rating = float(power_rating)
        self._hourly_rental_rate = float(hourly_rental_rate)
        
        if current_status not in ["Available", "Rented"]:
            raise ValueError("Status must be 'Available' or 'Rented'")
        self._current_status = current_status

    @property
    def equipment_id(self):
        return self._equipment_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def power_rating(self):
        return self._power_rating

    @power_rating.setter
    def power_rating(self, value):
        self._power_rating = float(value)

    @property
    def hourly_rental_rate(self):
        return self._hourly_rental_rate
        
    @hourly_rental_rate.setter
    def hourly_rental_rate(self, value):
        self._hourly_rental_rate = float(value)

    @property
    def current_status(self):
        return self._current_status

    @current_status.setter
    def current_status(self, value):
        if value not in ["Available", "Rented"]:
            raise ValueError("Status must be 'Available' or 'Rented'")
        self._current_status = value

    def to_dict(self):
        return {
            "equipment_id": self.equipment_id,
            "name": self.name,
            "power_rating": self.power_rating,
            "hourly_rental_rate": self.hourly_rental_rate,
            "current_status": self.current_status
        }
    
    @classmethod
    def from_dict(cls, data):
        # Lay du lieu tu dictionary (khong dung .get de dễ hiểu)
        eq_id = data["equipment_id"]
        
        if "name" in data:
            name = data["name"]
        else:
            name = ""
            
        power = float(data["power_rating"])
        rate = float(data["hourly_rental_rate"])
        
        if "current_status" in data:
            status = data["current_status"]
        else:
            status = "Available"
            
        # Tao doi tuong Equipment
        obj = cls(eq_id, name, power, rate, status)
        return obj

    def __str__(self):
        # Cong chuoi co ban de de doc hon f-string
        text = "ID: " + self.equipment_id + " | "
        text = text + "Name: " + self.name + " | "
        text = text + "Power: " + str(self.power_rating) + "W | "
        text = text + "Rate: $" + str(self.hourly_rental_rate) + "/hr | "
        text = text + "Status: " + self.current_status
        return text
