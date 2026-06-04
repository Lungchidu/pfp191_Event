import { useEffect, useState } from "react";
import { fetchCurrentUser, getAuthUrl } from "../config/auth";

/** Chỉ vào shop khi Python xác nhận session đăng nhập */
export default function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("checking"); // "checking" | "ok" | "error"
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const user = await fetchCurrentUser();
        if (cancelled) return;
        if (!user) {
          window.location.href = getAuthUrl();
          return;
        }
        setStatus("ok");
      } catch (err) {
        // Lỗi kết nối → server Flask chưa chạy
        if (cancelled) return;
        setErrorMsg("Không kết nối được server Python (Flask). Hãy chắc chắn đã chạy: python app.py");
        setStatus("error");
      }
    }

    check();
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") {
    return (
      <p style={{ textAlign: "center", padding: 40 }}>
        Đang kiểm tra đăng nhập với server Python...
      </p>
    );
  }

  if (status === "error") {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <p style={{ color: "red", fontWeight: "bold" }}>⚠️ {errorMsg}</p>
        <button
          onClick={() => window.location.reload()}
          style={{ marginTop: 10, padding: "8px 20px", cursor: "pointer" }}
        >
          Thử lại
        </button>
      </div>
    );
  }

  return children;
}
