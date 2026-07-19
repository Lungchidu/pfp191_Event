import sys
from equipment import Equipment, AudioEquipment, LightingEquipment, GeneralEquipment
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
            
            print("Select Equipment Category:")
            print("1. Audio")
            print("2. Lighting")
            print("3. General (Other)")
            cat_choice = input("Enter choice: ").strip()
            
            if cat_choice == '1':
                eq = AudioEquipment(eq_id, name, power, rate)
            elif cat_choice == '2':
                eq = LightingEquipment(eq_id, name, power, rate)
            else:
                eq = GeneralEquipment(eq_id, name, power, rate)
                
            self.equipment_dict[eq_id] = eq
            print("Equipment added successfully!")
        except ValueError as e:
            # Thông báo lỗi nhập liệu
            print("Invalid input: " + str(e))

    def update_equipment(self):
        print("\n--- Update Equipment ---")
        # Báo lỗi nếu chưa có dữ liệu (file không tồn tại hoặc rỗng)
        if len(self.equipment_dict) == 0:
            print("Error: No equipment data available (file might be missing or empty).")
            return
            
        query = input("Enter Equipment ID or Name to update: ").strip()
        
        eq = self.find_equipment(query)
        if eq == None:
            print("Equipment not found.")
            return
        
        # Hiển thị thông tin hiện tại
        print("Current details: " + str(eq))
        
        print("\n1. Edit Equipment (Name, Power, Rate)")
        print("2. Delete Equipment")
        print("3. Cancel")
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            try:
                new_name = input("Enter new Name (press enter to skip): ").strip()
                if new_name:
                    eq.name = new_name
                    
                new_power = input("Enter new Power Rating (press enter to skip): ").strip()
                if new_power:
                    eq.power_rating = float(new_power)
                    
                new_rate = input("Enter new Hourly Rental Rate (press enter to skip): ").strip()
                if new_rate:
                    eq.hourly_rental_rate = float(new_rate)
                    
                print("Equipment updated successfully!")
            except ValueError as e:
                print("Invalid input: " + str(e))
        elif choice == '2':
            confirm = input(f"Are you sure you want to delete '{eq.name}'? (Y/N): ").strip().upper()
            if confirm == 'Y':
                del self.equipment_dict[eq.equipment_id]
                print("Equipment deleted successfully!")
            else:
                print("Deletion cancelled.")
        else:
            print("Operation cancelled.")

    def search_equipment(self):
        print("\n--- Search Equipment ---")
        if len(self.equipment_dict) == 0:
            print("Error: No equipment data available (file might be missing or empty).")
            return
            
        query = input("Enter Equipment ID or Name to search: ").strip().lower()
        found = False
        for eq in self.equipment_dict.values():
            if query in eq.equipment_id.lower() or query in eq.name.lower():
                print(eq)
                found = True
        if not found:
            print("No matching equipment found.")

    def find_equipment(self, query):
        query = query.strip().lower()
        matches = []
        
        # Tìm tất cả các kết quả phù hợp (theo ID hoặc Tên)
        for eq in self.equipment_dict.values():
            if query in eq.equipment_id.lower() or query in eq.name.lower():
                matches.append(eq)
                
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            print("\nMultiple equipments found:")
            for i in range(len(matches)):
                print(str(i + 1) + ". " + str(matches[i]))
            
            # Yêu cầu người dùng chọn nếu có nhiều hơn 1 kết quả
            while True:
                choice_str = input("Select an equipment by number (or 0 to cancel): ").strip()
                if choice_str == '0':
                    return None
                try:
                    choice_idx = int(choice_str)
                    if choice_idx >= 1 and choice_idx <= len(matches):
                        return matches[choice_idx - 1]
                    else:
                        print("Invalid number. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")

    def filter_equipment(self):
        print("\n--- Filter Equipment ---")
        if len(self.equipment_dict) == 0:
            print("Error: No equipment data available (file might be missing or empty).")
            return
            
        print("1. By Status (Available/Rented)")
        print("2. By Hourly Rate Range")
        print("3. By Power Rating Range")
        print("4. By Name")
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
        elif choice == '4':
            query = input("Enter Name to filter: ").strip().lower()
            for eq in self.equipment_dict.values():
                if query in eq.name.lower():
                    print(eq)
                    found = True
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
                query = input("Enter Equipment ID or Name to add: ").strip()
                eq = self.find_equipment(query)
                if eq == None:
                    print("Equipment not found.")
                elif eq.current_status != "Available":
                    print("Equipment is not available.")
                else:
                    eid = eq.equipment_id
                    # Kiểm tra xem đã có trong giỏ chưa bằng vòng lặp
                    in_cart = False
                    for item in self.rental_cart:
                        if item == eid:
                            in_cart = True
                            
                    if in_cart:
                        print("Equipment already in cart.")
                    else:
                        self.rental_cart.append(eid)
                        print("Added to cart.")
            elif choice == '3':
                query = input("Enter Equipment ID or Name to remove: ").strip()
                eq = self.find_equipment(query)
                if eq == None:
                    print("Equipment not found.")
                else:
                    eid = eq.equipment_id
                    in_cart = False
                    for item in self.rental_cart:
                        if item == eid:
                            in_cart = True
                            
                    if in_cart:
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
        if len(self.rentals) == 0:
            print("\nError: No order data available (file might be missing or empty).")
            return
            
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
        query = input("Enter Order ID or Client Name to track: ").strip().lower()
        found = False
        for r in self.rentals:
            if query == r.rental_id.lower() or query in r.client_name.lower():
                print("\nOrder Details:")
                print(r)
                fees = r.calculate_fees(self.equipment_dict)
                print("Total Fees: $" + str(round(fees, 2)))
                print("Equipments:")
                for eid in r.equipment_ids:
                    if eid in self.equipment_dict:
                        print(" - " + str(self.equipment_dict[eid]))
                found = True
        if not found:
            print("Order not found.")

    def payment(self):
        query = input("Enter Order ID or Client Name for payment: ").strip().lower()
        matches = []
        for r in self.rentals:
            if query == r.rental_id.lower() or query in r.client_name.lower():
                matches.append(r)
                
        if len(matches) == 0:
            print("Order not found.")
            return
        elif len(matches) > 1:
            print("Found multiple orders. Please try again with the exact Order ID:")
            for m in matches:
                print(m)
            return
            
        r = matches[0]
        if r.status == "Paid":
            print("Order is already paid.")
        elif r.status == "Cancelled":
            print("Cannot pay for a cancelled order.")
        elif r.status == "Completed":
            print("Order is already completed.")
        else:
            fees = r.calculate_fees(self.equipment_dict)
            print("Total Amount Due: $" + str(round(fees, 2)))
            confirm = input("Confirm payment? (Y/N): ").strip().upper()
            if confirm == 'Y':
                r.status = "Paid"
                print("Payment successful. Order status updated to Paid.")
            else:
                print("Payment cancelled.")

    def cancel_order(self):
        query = input("Enter Order ID or Client Name to cancel: ").strip().lower()
        matches = []
        for r in self.rentals:
            if query == r.rental_id.lower() or query in r.client_name.lower():
                matches.append(r)
                
        if len(matches) == 0:
            print("Order not found.")
            return
        elif len(matches) > 1:
            print("Found multiple orders. Please try again with the exact Order ID:")
            for m in matches:
                print(m)
            return
            
        r = matches[0]
        if r.status == "Cancelled" or r.status == "Completed":
            print("Order cannot be cancelled because its status is " + r.status + ".")
        else:
            confirm = input("Are you sure you want to cancel order " + r.rental_id + "? (Y/N): ").strip().upper()
            if confirm == 'Y':
                r.status = "Cancelled"
                for eid in r.equipment_ids:
                    if eid in self.equipment_dict:
                        self.equipment_dict[eid].current_status = "Available"
                print("Order cancelled. Equipments are now available.")
            else:
                print("Cancellation aborted.")

    def book_equipment(self):
        print("\n--- Book Equipment ---")
        if len(self.equipment_dict) == 0:
            print("Error: No equipment data available (file might be missing or empty).")
            return
            
        query = input("Enter Equipment ID or Name to book: ").strip()
        eq = self.find_equipment(query)
        
        if eq == None:
            print("Equipment not found.")
            return
            
        if eq.current_status != "Available":
            print("Equipment is not available.")
            return
            
        eid = eq.equipment_id
        in_cart = False
        for item in self.rental_cart:
            if item == eid:
                in_cart = True
                
        if in_cart:
            print("Equipment already in cart.")
        else:
            self.rental_cart.append(eid)
            print("Successfully added '" + eq.name + "' to your cart!")
            print("Go to 'Rental Cart (Checkout)' to complete your order.")

    def data_analysis(self):
        print("\n--- Data Analysis ---")
        if len(self.equipment_dict) == 0 and len(self.rentals) == 0:
            print("Error: No data available to analyze (files might be missing or empty).")
            return
            
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
            print("1. Search Equipment")
            print("2. Filter Equipment")
            print("3. Book Equipment (Add to Cart)")
            print("4. Rental Cart (Checkout)")
            print("5. Order Management (Track, Pay, Cancel)")
            print("6. Data Analysis (Sorting)")
            print("7. Logout")
            print("8. Exit and Save")
            if self.auth.is_admin():
                print("9. Add Equipment (Admin)")
                print("10. Update Equipment (Admin)")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.search_equipment()
            elif choice == '2':
                self.filter_equipment()
            elif choice == '3':
                self.book_equipment()
            elif choice == '4':
                self.rental_cart_menu()
            elif choice == '5':
                self.order_management_menu()
            elif choice == '6':
                self.data_analysis()
            elif choice == '7':
                self.auth.logout()
                self.rental_cart = []
                print("Logged out successfully.")
                if not self.auth.auth_menu():
                    data_manager.save_equipment(self.equipment_dict)
                    data_manager.save_rentals(self.rentals)
                    print("Data saved. Exiting application.")
                    sys.exit(0)
            elif choice == '8':
                data_manager.save_equipment(self.equipment_dict)
                data_manager.save_rentals(self.rentals)
                print("Data saved. Exiting application.")
                sys.exit(0)
            elif choice == '9':
                if self.auth.is_admin():
                    self.add_equipment()
                else:
                    print("Invalid choice. Please try again.")
            elif choice == '10':
                if self.auth.is_admin():
                    self.update_equipment()
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = EventRentalApp()
    app.run()
