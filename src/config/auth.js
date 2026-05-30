/** Server Python Flask */
export const API_BASE =
  process.env.REACT_APP_API_URL || "http://localhost:5000";

export const AUTH_SERVER = API_BASE;
export const USER_KEY = "eventrent_user";

export function getStoredUsername() {
  return sessionStorage.getItem(USER_KEY) || "";
}

/** Sau khi Flask chuyển hướng: ...?username=ten */
export function saveUserFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const user = params.get("username");
  if (!user) return;

  sessionStorage.setItem(USER_KEY, user);
  params.delete("username");
  const rest = params.toString();
  const path = window.location.pathname;
  window.history.replaceState({}, "", rest ? `${path}?${rest}` : path);
}

export function clearStoredUser() {
  sessionStorage.removeItem(USER_KEY);
}

async function apiRequest(url, options = {}) {
  const username = getStoredUsername();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (username) {
    headers["X-Username"] = username;
  }

  const res = await fetch(`${API_BASE}${url}`, {
    credentials: "include",
    ...options,
    headers,
  });

  let data = {};
  try {
    data = await res.json();
  } catch {
    throw new Error(
      "Server Python chưa chạy hoặc trả về lỗi. Hãy mở terminal và chạy: python app.py"
    );
  }

  return { res, data };
}

/** Kiểm tra đăng nhập (session + dự phòng username) */
export async function fetchCurrentUser() {
  try {
    const { res, data } = await apiRequest("/api/me");
    if (res.ok && data.logged_in && data.username) {
      sessionStorage.setItem(USER_KEY, data.username);
      return data.username;
    }
    return getStoredUsername() || null;
  } catch {
    return getStoredUsername() || null;
  }
}

export function getAuthUrl() {
  return AUTH_SERVER;
}

export async function logout() {
  try {
    await apiRequest("/api/logout", { method: "POST" });
  } catch {
    /* bỏ qua nếu server tắt */
  }
  clearStoredUser();
  window.location.href = AUTH_SERVER;
}

export { apiRequest };
