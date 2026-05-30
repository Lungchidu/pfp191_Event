import { isLoggedIn, getAuthUrl } from "../config/auth";

/**
 * Chỉ cho vào trang mua sắm khi đã đăng nhập.
 * Chưa đăng nhập → chuyển về trang LoginandRegister (Flask).
 */
export default function ProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    window.location.href = getAuthUrl();
    return null;
  }
  return children;
}
