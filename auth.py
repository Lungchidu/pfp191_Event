import hashlib
import re
import data_manager


class Auth:
    """Handles user authentication: login, registration, and session management."""

    def __init__(self):
        self.users = data_manager.load_users()
        self.current_user = None
        # Ensure default admin account exists (password: admin123)
        if "admin" not in self.users:
            self.users["admin"] = {
                "username": "admin",
                "password": self._hash_password("admin123"),
                "role": "admin",
                "full_name": "Administrator",
                "email": "admin@event.com"
            }
            data_manager.save_users(self.users)

    # Mã hóa mật khẩu bằng SHA-256
    def _hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Kiểm tra định dạng email
    def _validate_email(self, email):
        """Basic email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result = re.match(pattern, email)
        if result:
            return True
        else:
            return False

    # Kiểm tra tên người dùng hợp lệ
    def _validate_username(self, username):
        """Username must be 3-20 characters, alphanumeric and underscores only."""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        result = re.match(pattern, username)
        if result:
            return True
        else:
            return False

    # Kiểm tra mật khẩu đủ dài
    def _validate_password(self, password):
        """Password must be at least 6 characters."""
        if len(password) >= 6:
            return True
        else:
            return False

    def login(self, username, password):
        """Attempt to log in with given credentials."""
        if username not in self.users:
            return False

        hashed = self._hash_password(password)
        user = self.users[username]

        # Support both hashed and plaintext passwords (for migration)
        if user["password"] == hashed or user["password"] == password:
            # If password was stored as plaintext, upgrade to hash
            if user["password"] == password and user["password"] != hashed:
                user["password"] = hashed
                data_manager.save_users(self.users)

            self.current_user = user
            return True

        return False

    def register(self, username, password, full_name, email, role="user"):
        """
        Register a new user account.
        Returns (success: bool, message: str).
        """
        # Validate username
        if not self._validate_username(username):
            return False, "Username must be 3-20 characters (letters, numbers, underscores only)."

        # Check if username already exists
        if username in self.users:
            return False, "Username already exists. Please choose another."

        # Validate password
        if not self._validate_password(password):
            return False, "Password must be at least 6 characters."

        # Validate full name
        if not full_name or not full_name.strip():
            return False, "Full name cannot be empty."

        # Validate email
        if not self._validate_email(email):
            return False, "Invalid email format."

        # Create user
        self.users[username] = {
            "username": username,
            "password": self._hash_password(password),
            "role": role,
            "full_name": full_name.strip(),
            "email": email.strip()
        }

        data_manager.save_users(self.users)
        return True, "Registration successful! You can now log in."

    def logout(self):
        """Log out the current user."""
        self.current_user = None

    # Kiểm tra đã đăng nhập chưa
    def is_logged_in(self):
        """Check if a user is currently logged in."""
        if self.current_user is not None:
            return True
        else:
            return False

    # Kiểm tra có phải admin không
    def is_admin(self):
        """Check if the current user has admin role."""
        if self.current_user is None:
            return False
        # Kiểm tra role có trong dict không
        if "role" in self.current_user:
            role = self.current_user["role"]
        else:
            role = ""
        if role == "admin":
            return True
        else:
            return False

    # Lấy tên đăng nhập hiện tại
    def get_current_username(self):
        """Get the username of the currently logged-in user."""
        if self.current_user:
            # Kiểm tra key "username" có trong dict không
            if "username" in self.current_user:
                return self.current_user["username"]
            else:
                return ""
        return ""

    # Lấy họ tên đầy đủ hiện tại
    def get_current_fullname(self):
        """Get the full name of the currently logged-in user."""
        if self.current_user:
            # Kiểm tra key "full_name" có trong dict không
            if "full_name" in self.current_user:
                return self.current_user["full_name"]
            else:
                return ""
        return ""

    def auth_menu(self):
        """
        Display login/register menu.
        Returns True if user successfully logs in, False if user wants to exit.
        """
        while True:
            print("\n" + "=" * 40)
            print("  Event Equipment Rental & Logistics")
            print("=" * 40)
            print("1. Login")
            print("2. Register")
            print("3. Exit")

            choice = input("\nEnter your choice: ").strip()

            if choice == '1':
                print("\n--- Login ---")
                username = input("Username: ").strip()
                password = input("Password: ").strip()

                if not username or not password:
                    print("Username and password cannot be empty.")
                    continue

                if self.login(username, password):
                    # Thay f-string bằng nối chuỗi
                    print("\nWelcome back, " + self.get_current_fullname() + "!")
                    return True
                else:
                    print("Invalid username or password. Please try again.")

            elif choice == '2':
                print("\n--- Register New Account ---")
                username = input("Username (3-20 chars, letters/numbers/underscores): ").strip()
                password = input("Password (at least 6 characters): ").strip()
                confirm_password = input("Confirm Password: ").strip()

                if password != confirm_password:
                    print("Passwords do not match. Please try again.")
                    continue

                full_name = input("Full Name: ").strip()
                email = input("Email: ").strip()

                success, message = self.register(username, password, full_name, email)
                print(message)

            elif choice == '3':
                print("Goodbye!")
                return False

            else:
                print("Invalid choice. Please try again.")
