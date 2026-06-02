const AUTH_SERVER =
  process.env.REACT_APP_AUTH_URL || "http://localhost:5000";

export { AUTH_SERVER };
export const TOKEN_KEY = "token";
export const USER_KEY = "username";

export function isLoggedIn() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    // Kiểm tra token còn hạn không
    return payload.exp > Date.now() / 1000;
  } catch {
    return false;
  }
}

export function getUsername() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return localStorage.getItem(USER_KEY) || "";
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.username;
  } catch {
    return "";
  }
}

export function getAuthUrl() {
  return "/auth";
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.location.href = "/auth";
}

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
