import sys
from equipment import Equipment
from rental import Rental
from auth import Auth
import data_manager

class EventRentalApp:
    def __init__(self):
        self.equipment_dict = data_manager.load_equipment()
        self.rentals = data_manager.load_rentals()
        self.auth = Auth()
        self.rental_cart = []

    def add_equipment(self):
        print("\n--- Add New Equipment ---")
        eq_id = input("Enter Equipment ID: ").strip()
        if not eq_id:
            print("ID cannot be empty.")
            return
        if eq_id in self.equipment_dict:
            print("Equipment ID already exists.")
            return
            
        name = input("Enter Equipment Name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        try:
            power = float(input("Enter Power Rating (W): "))
            rate = float(input("Enter Hourly Rental Rate ($): "))
            eq = Equipment(eq_id, name, power, rate)
            self.equipment_dict[eq_id] = eq
            print("Equipment added successfully!")
        except ValueError as e:
            # Thông báo lỗi nhập liệu
            print("Invalid input: " + str(e))

    def update_equipment(self):
        print("\n--- Update Equipment ---")
        eq_id = input("Enter Equipment ID to update: ").strip()
        if eq_id not in self.equipment_dict:
            print("Equipment not found.")
            return
        
        eq = self.equipment_dict[eq_id]
        # Hiển thị thông tin hiện tại
        print("Current details: " + str(eq))
        
        try:
            new_power = input("Enter new Power Rating (press enter to skip): ").strip()
            if new_power:
                eq.power_rating = float(new_power)
                
            new_rate = input("Enter new Hourly Rental Rate (press enter to skip): ").strip()
            if new_rate:
                eq.hourly_rental_rate = float(new_rate)
                
            print("Equipment updated successfully!")
        except ValueError as e:
            print("Invalid input: " + str(e))

    def search_equipment(self):
        print("\n--- Search Equipment ---")
        query = input("Enter Equipment ID or Name to search: ").strip().lower()
        found = False
        for eq in self.equipment_dict.values():
            if query in eq.equipment_id.lower() or query in eq.name.lower():
                print(eq)
                found = True
        if not found:
            print("No matching equipment found.")

    def filter_equipment(self):
        print("\n--- Filter Equipment ---")
        print("1. By Status (Available/Rented)")
        print("2. By Hourly Rate Range")
        print("3. By Power Rating Range")
        choice = input("Enter choice: ").strip()
        
        found = False
        if choice == '1':
            status = input("Enter Status (Available/Rented): ").strip().capitalize()
            for eq in self.equipment_dict.values():
                if eq.current_status == status:
                    print(eq)
                    found = True
        elif choice == '2':
            try:
                min_r = float(input("Min Rate: "))
                max_r = float(input("Max Rate: "))
                for eq in self.equipment_dict.values():
                    # Kiểm tra giá thuê nằm trong khoảng
                    if eq.hourly_rental_rate >= min_r and eq.hourly_rental_rate <= max_r:
                        print(eq)
                        found = True
            except ValueError:
                print("Invalid input.")
                return
        elif choice == '3':
            try:
                min_p = float(input("Min Power: "))
                max_p = float(input("Max Power: "))
                for eq in self.equipment_dict.values():
                    # Kiểm tra công suất nằm trong khoảng
                    if eq.power_rating >= min_p and eq.power_rating <= max_p:
                        print(eq)
                        found = True
            except ValueError:
                print("Invalid input.")
                return
        else:
            print("Invalid choice.")
            return
            
        if not found:
            print("No equipment matched your filter criteria.")

    def rental_cart_menu(self):
        while True:
            print("\n--- Rental Cart ---")
            # Đếm số lượng trong giỏ hàng
            cart_count = len(self.rental_cart)
            print("Items in cart: " + str(cart_count))
            print("1. View Cart")
            print("2. Add Equipment to Cart")
            print("3. Remove Equipment from Cart")
            print("4. Clear Cart")
            print("5. Checkout (Create Order)")
            print("6. Back to Main Menu")
            
            choice = input("Enter choice: ").strip()
            if choice == '1':
                if not self.rental_cart:
                    print("Cart is empty.")
                else:
                    for eid in self.rental_cart:
                        print(self.equipment_dict[eid])
            elif choice == '2':
                eid = input("Enter Equipment ID to add: ").strip()
                if eid not in self.equipment_dict:
                    print("Equipment not found.")
                elif self.equipment_dict[eid].current_status != "Available":
                    print("Equipment is not available.")
                elif eid in self.rental_cart:
                    print("Equipment already in cart.")
                else:
                    self.rental_cart.append(eid)
                    print("Added to cart.")
            elif choice == '3':
                eid = input("Enter Equipment ID to remove: ").strip()
                if eid in self.rental_cart:
                    self.rental_cart.remove(eid)
                    print("Removed from cart.")
                else:
                    print("Equipment not in cart.")
            elif choice == '4':
                # Xóa giỏ hàng
                self.rental_cart = []
                print("Cart cleared.")
            elif choice == '5':
                self.checkout()
            elif choice == '6':
                break
            else:
                print("Invalid choice.")

    def checkout(self):
        if not self.rental_cart:
            print("Cart is empty. Cannot checkout.")
            return
            
        print("\n--- Checkout ---")
        rental_id = input("Enter new Order ID: ").strip()

        # Kiểm tra mã đơn hàng đã tồn tại chưa
        id_exists = False
        for r in self.rentals:
            if r.rental_id == rental_id:
                id_exists = True
                break
        if id_exists:
            print("Order ID already exists.")
            return
            
        client = input("Enter Client Name: ").strip()
        start = input("Enter Start Date (YYYY-MM-DD): ").strip()
        end = input("Enter Expected Return Date (YYYY-MM-DD): ").strip()
        
        for eid in self.rental_cart:
            if self.equipment_dict[eid].current_status != "Available":
                print("Error: Equipment " + eid + " is no longer available. Please remove it from cart.")
                return
        
        # Sao chép danh sách giỏ hàng
        cart_copy = []
        for item in self.rental_cart:
            cart_copy.append(item)
                
        try:
            r = Rental(rental_id, client, start, end, cart_copy, status="Pending")
            for eid in self.rental_cart:
                self.equipment_dict[eid].current_status = "Rented"
                
            self.rentals.append(r)
            fees = r.calculate_fees(self.equipment_dict)
            # Hiển thị phí ước tính
            print("Order created successfully! Estimated fee: $" + str(round(fees, 2)) + ". Status: Pending.")
            self.rental_cart = []
        except Exception as e:
            print("Failed to create order: " + str(e))

    def order_management_menu(self):
        while True:
            print("\n--- Order Management ---")
            print("1. Track Order")
            print("2. Payment")
            print("3. Cancel Order")
            print("4. Back to Main Menu")
            
            choice = input("Enter choice: ").strip()
            if choice == '1':
                self.track_order()
            elif choice == '2':
                self.payment()
            elif choice == '3':
                self.cancel_order()
            elif choice == '4':
                break
            else:
                print("Invalid choice.")

    def track_order(self):
        rid = input("Enter Order ID to track: ").strip()
        for r in self.rentals:
            if r.rental_id == rid:
                print("\nOrder Details:")
                print(r)
                fees = r.calculate_fees(self.equipment_dict)
                # Hiển thị tổng phí
                print("Total Fees: $" + str(round(fees, 2)))
                print("Equipments:")
                for eid in r.equipment_ids:
                    if eid in self.equipment_dict:
                        print(" - " + str(self.equipment_dict[eid]))
                return
        print("Order not found.")

    def payment(self):
        rid = input("Enter Order ID for payment: ").strip()
        for r in self.rentals:
            if r.rental_id == rid:
                if r.status == "Paid":
                    print("Order is already paid.")
                elif r.status == "Cancelled":
                    print("Cannot pay for a cancelled order.")
                elif r.status == "Completed":
                    print("Order is already completed.")
                else:
                    fees = r.calculate_fees(self.equipment_dict)
                    # Hiển thị số tiền cần thanh toán
                    print("Total Amount Due: $" + str(round(fees, 2)))
                    confirm = input("Confirm payment? (Y/N): ").strip().upper()
                    if confirm == 'Y':
                        r.status = "Paid"
                        print("Payment successful. Order status updated to Paid.")
                    else:
                        print("Payment cancelled.")
                return
        print("Order not found.")

    def cancel_order(self):
        rid = input("Enter Order ID to cancel: ").strip()
        for r in self.rentals:
            if r.rental_id == rid:
                # Kiểm tra trạng thái đơn hàng
                if r.status == "Cancelled" or r.status == "Completed":
                    print("Order cannot be cancelled because its status is " + r.status + ".")
                else:
                    confirm = input("Are you sure you want to cancel order " + rid + "? (Y/N): ").strip().upper()
                    if confirm == 'Y':
                        r.status = "Cancelled"
                        for eid in r.equipment_ids:
                            if eid in self.equipment_dict:
                                self.equipment_dict[eid].current_status = "Available"
                        print("Order cancelled. Equipments are now available.")
                    else:
                        print("Cancellation aborted.")
                return
        print("Order not found.")

    def data_analysis(self):
        print("\n--- Data Analysis ---")
        print("1. Sort Equipment by Rental Rate")
        print("2. Sort Equipment by Power Rating")
        print("3. Sort Orders by Client Name")
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            # Sắp xếp thiết bị theo giá thuê - dùng hàm lấy giá trị
            def get_rental_rate(equipment):
                return equipment.hourly_rental_rate

            eq_list = []
            for eq in self.equipment_dict.values():
                eq_list.append(eq)
            sorted_eq = sorted(eq_list, key=get_rental_rate)
            for eq in sorted_eq:
                print(eq)
        elif choice == '2':
            # Sắp xếp thiết bị theo công suất - dùng hàm lấy giá trị
            def get_power_rating(equipment):
                return equipment.power_rating

            eq_list = []
            for eq in self.equipment_dict.values():
                eq_list.append(eq)
            sorted_eq = sorted(eq_list, key=get_power_rating)
            for eq in sorted_eq:
                print(eq)
        elif choice == '3':
            # Sắp xếp đơn hàng theo tên khách hàng - dùng hàm lấy giá trị
            def get_client_name(rental):
                return rental.client_name.lower()

            sorted_r = sorted(self.rentals, key=get_client_name)
            for r in sorted_r:
                print(r)
        else:
            print("Invalid choice.")

    def run(self):
        if not self.auth.auth_menu():
            sys.exit(0)

        while True:
            # Xác định vai trò người dùng
            if self.auth.is_admin():
                role_label = "Admin"
            else:
                role_label = "User"

            print("\n" + "=" * 40)
            print("Event Equipment Rental & Logistics")
            # Hiển thị thông tin đăng nhập
            print("Logged in as: " + self.auth.get_current_fullname() + " (" + role_label + ")")
            print("=" * 40)
            print("1. Add Equipment")
            print("2. Update Equipment")
            print("3. Search Equipment")
            print("4. Filter Equipment")
            print("5. Rental Cart (Checkout)")
            print("6. Order Management (Track, Pay, Cancel)")
            print("7. Data Analysis (Sorting)")
            print("8. Logout")
            print("9. Exit and Save")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.add_equipment()
            elif choice == '2':
                self.update_equipment()
            elif choice == '3':
                self.search_equipment()
            elif choice == '4':
                self.filter_equipment()
            elif choice == '5':
                self.rental_cart_menu()
            elif choice == '6':
                self.order_management_menu()
            elif choice == '7':
                self.data_analysis()
            elif choice == '8':
                self.auth.logout()
                self.rental_cart = []
                print("Logged out successfully.")
                if not self.auth.auth_menu():
                    data_manager.save_equipment(self.equipment_dict)
                    data_manager.save_rentals(self.rentals)
                    print("Data saved. Exiting application.")
                    sys.exit(0)
            elif choice == '9':
                data_manager.save_equipment(self.equipment_dict)
                data_manager.save_rentals(self.rentals)
                print("Data saved. Exiting application.")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = EventRentalApp()
    app.run()
