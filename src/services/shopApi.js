import { API_BASE, getStoredUsername, parseApiResponse } from "../config/auth";

function buildHeaders(extra = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...extra,
  };
  const username = getStoredUsername();
  if (username) {
    headers["X-Username"] = username;
  }
  const token = localStorage.getItem("token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    credentials: "include",
    ...options,
    headers: buildHeaders(options.headers),
  });

  let data = {};
  try {
    data = await parseApiResponse(res);
  } catch (err) {
    throw new Error(
      err.message ||
        "Không kết nối được server Python. Chạy: cd LoginandRegister/myapp && python app.py"
    );
  }

  if (data.maintenance) {
    window.dispatchEvent(
      new CustomEvent("maintenance_mode", { detail: data.message })
    );
    throw new Error(data.message || "Hệ thống đang bảo trì");
  }

  if (!res.ok || data.success === false) {
    throw new Error(data.message || "Lỗi server Python");
  }
  return data;
}

function filtersToQuery(filters) {
  const params = new URLSearchParams();
  if (filters.query) params.set("q", filters.query);
  if (filters.categoryId) params.set("cat", String(filters.categoryId));
  if (filters.location) params.set("loc", filters.location);
  if (filters.minRating) params.set("rating", String(filters.minRating));
  if (filters.maxPrice) params.set("max", String(filters.maxPrice));
  if (filters.flashOnly) params.set("flash", "1");
  if (filters.sortBy && filters.sortBy !== "default") {
    params.set("sort", filters.sortBy);
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchUiData() {
  const data = await request("/api/ui");
  return data;
}

export async function fetchProducts(filters = {}) {
  const data = await request(`/api/products${filtersToQuery(filters)}`);
  return data.products;
}

export async function fetchFlashProducts() {
  const data = await request("/api/products/flash");
  return data.products;
}

export async function fetchCategories() {
  const data = await request("/api/categories");
  return data.categories;
}

export async function fetchLocations() {
  const data = await request("/api/locations");
  return data.locations;
}

export async function fetchProductDetail(id) {
  const data = await request(`/api/products/${id}`);
  return { product: data.product, related: data.related };
}

export async function fetchCart() {
  const data = await request("/api/cart");
  return data.items;
}

export async function addCartItem(productId, quantity = 1, days = 1) {
  const data = await request("/api/cart", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, quantity, days }),
  });
  return data.items;
}

export async function updateCartItemApi(productId, patch) {
  const data = await request(`/api/cart/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
  return data.items;
}

export async function removeCartItemApi(productId) {
  const data = await request(`/api/cart/${productId}`, { method: "DELETE" });
  return data.items;
}

export async function checkoutCart(items = [], note = "", profileData = {}) {
  return request("/api/checkout", {
    method: "POST",
    body: JSON.stringify({
      items: items.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
        days: item.days,
      })),
      note,
      ...profileData
    }),
  });
}

export async function fetchOrders() {
  const data = await request("/api/orders");
  return data.orders;
}

export async function fetchProfile() {
  const data = await request("/api/profile");
  return data.profile;
}

export async function updateProfile(profileData) {
  const data = await request("/api/profile", {
    method: "POST",
    body: JSON.stringify(profileData),
  });
  return data;
}
