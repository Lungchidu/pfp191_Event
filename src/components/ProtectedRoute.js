import { useEffect, useState } from "react";
import { fetchCurrentUser, getAuthUrl } from "../config/auth";

export default function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("checking");
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
        if (cancelled) return;
        setStatus("error");
        setErrorMsg(
          err.message ||
            "Không kết nối được server Python (http://localhost:5000)"
        );
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
        Đang kiểm tra đăng nhập...
      </p>
    );
  }

  if (status === "error") {
    return (
      <div style={{ maxWidth: 480, margin: "60px auto", padding: 24 }}>
        <h2>Không mở được trang shop</h2>
        <p>{errorMsg}</p>
        <ol>
          <li>Mở terminal, chạy backend Python:</li>
        </ol>
        <pre
          style={{
            background: "#f4f4f4",
            padding: 12,
            borderRadius: 8,
            overflow: "auto",
          }}
        >
          cd LoginandRegister\myapp{"\n"}
          pip install -r ..\requirements.txt{"\n"}
          python app.py
        </pre>
        <p>Sau đó đăng nhập tại http://localhost:5000</p>
        <button
          type="button"
          onClick={() => {
            window.location.href = getAuthUrl();
          }}
        >
          Mở trang đăng nhập
        </button>
      </div>
    );
  }

  return children;
}
