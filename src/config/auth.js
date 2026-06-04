/** Server Python Flask — toàn bộ backend */
export const API_BASE =
  process.env.REACT_APP_API_URL || "http://localhost:5000";

export const AUTH_SERVER = API_BASE;

async function apiRequest(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  return { res, data };
}

/** Kiểm tra đã đăng nhập (session Python) */
export async function fetchCurrentUser() {
  const { res, data } = await apiRequest("/api/me");
  if (!res.ok || !data.logged_in) return null;
  return data.username;
}

export function getAuthUrl() {
  return AUTH_SERVER;
}

export async function logout() {
  await apiRequest("/api/logout", { method: "POST" });
  window.location.href = AUTH_SERVER;
}
