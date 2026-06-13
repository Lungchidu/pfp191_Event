import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { PRODUCTS } from "../data/mockData";
import { isLoggedIn } from "../config/auth";
import { fetchProducts } from "../services/shopApi";
 
// ─── Không còn import filterProducts nữa ───────────────────
 
const CART_KEY = "eventrent_cart";
const AppContext = createContext(null);
 
function loadCart() {
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
 
export function AppProvider({ children }) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [cart, setCart] = useState(loadCart);
  const [toast, setToast] = useState(null);
 
  // ─── State mới: kết quả lọc từ Python backend ──────────
  const [filteredProducts, setFilteredProducts] = useState(PRODUCTS);
  const [loadingProducts, setLoadingProducts] = useState(false);
 
  // ─── Đọc filters từ URL (giữ nguyên như cũ) ────────────
  const filters = useMemo(
    () => ({
      query:      searchParams.get("q")      || "",
      categoryId: searchParams.get("cat")    ? Number(searchParams.get("cat")) : null,
      location:   searchParams.get("loc")    || "",
      minRating:  Number(searchParams.get("rating") || 0),
      maxPrice:   searchParams.get("max")    ? Number(searchParams.get("max")) : null,
      flashOnly:  searchParams.get("flash")  === "1",
      sortBy:     searchParams.get("sort")   || "default",
      rentalDate: searchParams.get("date")   || "",
    }),
    [searchParams]
  );
 
  // ─── Mỗi khi filters thay đổi → gọi Python backend ────
  useEffect(() => {
    setLoadingProducts(true);
    fetchProducts(filters)
      .then((products) => setFilteredProducts(products))
      .catch(() => {
        // Nếu backend chưa chạy → fallback dùng mockData
        setFilteredProducts(PRODUCTS);
      })
      .finally(() => setLoadingProducts(false));
  }, [filters]);
 
  // ─── Cart ───────────────────────────────────────────────
  const cartCount = useMemo(
    () => cart.reduce((sum, item) => sum + item.quantity, 0),
    [cart]
  );
 
  const cartTotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.price * item.quantity * item.days, 0),
    [cart]
  );
 
  useEffect(() => {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart]);
 
  // ─── Toast ──────────────────────────────────────────────
  const showToast = useCallback((message) => {
    setToast(message);
    const timer = setTimeout(() => setToast(null), 2800);
    return () => clearTimeout(timer);
  }, []);
 
  // ─── Cập nhật URL params (giữ nguyên như cũ) ───────────
  const updateFilters = useCallback(
    (patch, options = {}) => {
      const { scrollToCatalog = false } = options;
      const next = new URLSearchParams(searchParams);
 
      Object.entries(patch).forEach(([key, value]) => {
        const paramMap = {
          query:      "q",
          categoryId: "cat",
          location:   "loc",
          minRating:  "rating",
          maxPrice:   "max",
          flashOnly:  "flash",
          sortBy:     "sort",
          rentalDate: "date",
        };
        const param = paramMap[key] || key;
 
        if (value === null || value === "" || value === 0 || value === false) {
          next.delete(param);
        } else if (key === "flashOnly") {
          if (value) next.set(param, "1");
          else next.delete(param);
        } else {
          next.set(param, String(value));
        }
      });
 
      setSearchParams(next, { replace: true });
 
      if (scrollToCatalog) {
        requestAnimationFrame(() => {
          document.getElementById("catalog")?.scrollIntoView({ behavior: "smooth" });
        });
      }
    },
    [searchParams, setSearchParams]
  );
 
  // ─── search: cập nhật URL → useEffect tự gọi backend ──
  const search = useCallback(
    (query) => {
      updateFilters({ query }, { scrollToCatalog: true });
    },
    [updateFilters]
  );
 
  // ─── filterByCategory: cập nhật URL → useEffect tự gọi backend
  const filterByCategory = useCallback(
    (categoryId) => {
      updateFilters(
        { categoryId: categoryId || null, query: "" },
        { scrollToCatalog: Boolean(categoryId) }
      );
    },
    [updateFilters]
  );
 
  // ─── filterByKeyword: cập nhật URL → useEffect tự gọi backend
  const filterByKeyword = useCallback(
    (keyword) => {
      updateFilters({ query: keyword }, { scrollToCatalog: true });
    },
    [updateFilters]
  );
 
  const clearFilters = useCallback(() => {
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);
 
  // ─── Navigation ─────────────────────────────────────────
  const goToProduct = useCallback(
    (id) => navigate(`/product/${id}`),
    [navigate]
  );
 
  const getProduct = useCallback(
    (id) => PRODUCTS.find((p) => p.id === Number(id)),
    []
  );
 
  // ─── Cart actions ───────────────────────────────────────
  const addToCart = useCallback(
    (product, quantity = 1, days = 1) => {
      if (!isLoggedIn()) {
        alert("Bạn cần đăng nhập hoặc đăng ký để thuê hàng!");
        navigate("/auth?mode=login");
        return;
      }
 
      setCart((prev) => {
        const existing = prev.find((i) => i.id === product.id);
        if (existing) {
          return prev.map((i) =>
            i.id === product.id
              ? { ...i, quantity: i.quantity + quantity, days: Math.max(i.days, days) }
              : i
          );
        }
        return [
          ...prev,
          {
            id:       product.id,
            name:     product.name,
            price:    product.price,
            image:    product.image,
            location: product.location,
            quantity,
            days,
          },
        ];
      });
      showToast(`Đã thêm "${product.name}" vào giỏ thuê`);
    },
    [showToast, navigate]
  );
 
  const updateCartItem = useCallback((id, patch) => {
    setCart((prev) =>
      prev
        .map((item) => (item.id === id ? { ...item, ...patch } : item))
        .filter((item) => item.quantity > 0)
    );
  }, []);
 
  const removeFromCart = useCallback(
    (id) => {
      setCart((prev) => prev.filter((item) => item.id !== id));
      showToast("Đã xóa khỏi giỏ thuê");
    },
    [showToast]
  );

  const clearCart = useCallback(() => {
    setCart([]);
    localStorage.removeItem(CART_KEY);
  }, []);
 
  // ─── Expose ra ngoài ────────────────────────────────────
  const value = {
    filters,
    filteredProducts,
    loadingProducts,   // có thể dùng để hiện spinner
    cart,
    cartCount,
    cartTotal,
    toast,
    search,
    updateFilters,
    filterByCategory,
    filterByKeyword,
    clearFilters,
    goToProduct,
    getProduct,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    showToast,
    navigate,
  };
 
  return (
    <AppContext.Provider value={value}>{children}</AppContext.Provider>
  );
}
 
export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error("useApp must be used within AppProvider");
  }
  return ctx;
}