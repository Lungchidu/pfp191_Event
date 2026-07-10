import bcrypt
import os
from database import CustomerDatabase

def create_admin():
    db = CustomerDatabase()
    db.init_tables()
    conn = db.connect()
    
    username = "adc@bua.nhan"
    password = "quangbolahut"
    
    existing = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        print("Admin user already exists.")
        # Make sure role is admin
        conn.execute("UPDATE users SET role='admin' WHERE username=?", (username,))
    else:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, 'admin')
        )
        print("Admin user created successfully.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_admin()
