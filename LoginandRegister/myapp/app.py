from flask import Flask, request, jsonify, render_template
import sqlite3
import bcrypt

app = Flask(__name__)
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_FILE)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Vui lòng nhập đầy đủ!"})

    conn = get_db()
    existing = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "Tài khoản đã tồn tại!"})

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Đăng ký thành công!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = get_db()
    row = conn.execute("SELECT password FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    # Gộp chung 1 thông báo, tránh lộ tài khoản có tồn tại không
    if not row or not bcrypt.checkpw(password.encode(), row[0].encode()):
        return jsonify({"success": False, "message": "Tài khoản hoặc mật khẩu không đúng!"})

    return jsonify({"success": True, "message": f"Chào mừng {username}!"})

@app.route("/")
def index():
    return render_template("index.html")  # ← đã sửa

if __name__ == "__main__":
    init_db()
    app.run(debug=True)