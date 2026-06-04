import { API_BASE } from "../config/auth";

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok || data.success === false) {
    throw new Error(data.message || "Lỗi kết nối server Python");
  }
  return data;
}

/** Chuyển bộ lọc URL thành query cho Python */
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
  return request("/api/ui");
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

export async function checkoutCart() {
  return request("/api/checkout", { method: "POST" });
}
