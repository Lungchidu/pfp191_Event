/** Địa chỉ server đăng nhập (Flask - thư mục LoginandRegister) */
export const AUTH_SERVER =
  process.env.REACT_APP_AUTH_URL || "http://localhost:5000";
export const USER_KEY = "username";

export function isLoggedIn() {
  return Boolean(localStorage.getItem(USER_KEY));
}

export function getAuthUrl() {
  return "/auth";
}

export function logout() {
  localStorage.removeItem(USER_KEY);
  window.location.href = "/auth";
}

/** Lưu username khi Flask chuyển hướng về shop (?username=...) */
export function saveUserFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const user = params.get("username");
  if (!user) return;
  localStorage.setItem(USER_KEY, user);
  params.delete("username");
  const rest = params.toString();
  const path = window.location.pathname;
  window.history.replaceState({}, "", rest ? `${path}?${rest}` : path);
}
