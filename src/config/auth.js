/**
 * Backend Flask Python — luôn gọi trực tiếp port 5000 (CORS đã bật trong app.py).
 * React có thể chạy port 3000/3001/3002... không ảnh hưởng.
 * Production: set REACT_APP_AUTH_URL trong .env
 */
const DEFAULT_API = "http://localhost:5000";

function getApiBase() {
  const fromEnv = process.env.REACT_APP_AUTH_URL;
  if (fromEnv) {
    return fromEnv.replace(/\/$/, "");
  }
  return DEFAULT_API;
}

const AUTH_SERVER = getApiBase();

export const API_BASE = (
  process.env.REACT_APP_API_URL || AUTH_SERVER
).replace(/\/$/, "");

export { AUTH_SERVER };
export const TOKEN_KEY = "token";
export const USER_KEY = "username";

/** Đọc JSON từ Flask — báo lỗi rõ nếu nhận HTML (proxy/React trả nhầm trang). */
export async function parseApiResponse(res) {
  const text = await res.text();
  const trimmed = text.trim();

  if (trimmed.startsWith("<!DOCTYPE") || trimmed.startsWith("<html")) {
    throw new Error(
      "Server trả về trang web thay vì JSON. Hãy chạy backend Python:\n" +
        "cd LoginandRegister/myapp\npython app.py"
    );
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(
      trimmed.slice(0, 100) || "Phản hồi server không hợp lệ"
    );
  }
}

export function isLoggedIn() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
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

export function getStoredUsername() {
  return getUsername();
}

export function getAuthUrl() {
  return "/auth";
}

export function getFlaskAuthUrl() {
  const shopOrigin =
    typeof window !== "undefined" ? window.location.origin : "";
  const qs = shopOrigin
    ? `?shop_url=${encodeURIComponent(shopOrigin)}`
    : "";
  return `${AUTH_SERVER}${qs}`;
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.location.href = "/auth";
}

export function saveUserFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const user = params.get("username");
  const token = params.get("token");
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  }
  if (user) {
    localStorage.setItem(USER_KEY, user);
  }
  if (!user && !token) return;
  params.delete("username");
  params.delete("token");
  const rest = params.toString();
  const path = window.location.pathname;
  window.history.replaceState({}, "", rest ? `${path}?${rest}` : path);
}

export async function verifyWithServer() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;
  try {
    const res = await fetch(`${AUTH_SERVER}/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });
    const data = await parseApiResponse(res);
    if (!data.success) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    return data.success === true;
  } catch {
    return false;
  }
}
