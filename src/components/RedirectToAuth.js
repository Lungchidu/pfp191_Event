import { useEffect } from "react";
import { getAuthUrl } from "../config/auth";

/** Chuyển sang trang đăng nhập Flask (LoginandRegister) */
export default function RedirectToAuth() {
  useEffect(() => {
    window.location.href = getAuthUrl();
  }, []);

  return <p style={{ textAlign: "center", padding: 40 }}>Đang chuyển đến trang đăng nhập...</p>;
}
