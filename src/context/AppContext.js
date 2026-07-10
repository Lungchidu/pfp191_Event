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
import { translateProduct } from "../data/i18n";

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
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "vi");

  const changeLang = useCallback((newLang) => {
    setLang(newLang);
    localStorage.setItem("lang", newLang);
  }, []);

 
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
    // Không lọc danh mục và query ở backend để xử lý client-side cho đa ngôn ngữ
    const apiFilters = { ...filters, categoryId: null, query: "" };
    fetchProducts(apiFilters)
      .then((products) => {
        let sorted = [...products];

        // Lọc theo query client-side với đa ngôn ngữ
        if (filters.query) {
          const q = filters.query.toLowerCase();
          sorted = sorted.filter((p) => {
            const translated = translateProduct(p, lang);
            return (
              translated.name.toLowerCase().includes(q) ||
              translated.description.toLowerCase().includes(q) ||
              (translated.tags && translated.tags.some((t) => t.toLowerCase().includes(q)))
            );
          });
        }

        if (filters.categoryId) {
          const matched = sorted.filter(
            (p) =>
              p.categoryId === filters.categoryId ||
              p.category_id === filters.categoryId
          );
          const unmatched = sorted.filter(
            (p) =>
              p.categoryId !== filters.categoryId &&
              p.category_id !== filters.categoryId
          );
          sorted = [...matched, ...unmatched];
        }
        setFilteredProducts(sorted);
      })
      .catch(() => {
        // Nếu backend chưa chạy → fallback dùng mockData
        let result = [...PRODUCTS];
        if (filters.query) {
          const q = filters.query.toLowerCase();
          result = result.filter((p) => {
            const translated = translateProduct(p, lang);
            return (
              translated.name.toLowerCase().includes(q) ||
              translated.description.toLowerCase().includes(q) ||
              (translated.tags && translated.tags.some((t) => t.toLowerCase().includes(q)))
            );
          });
        }
        if (filters.location) {
          result = result.filter((p) => p.location === filters.location);
        }
        if (filters.minRating > 0) {
          result = result.filter((p) => p.rating >= filters.minRating);
        }
        if (filters.maxPrice) {
          result = result.filter((p) => p.price <= filters.maxPrice);
        }
        if (filters.flashOnly) {
          result = result.filter((p) => p.isFlash);
        }

        // Sắp xếp theo lựa chọn sort
        if (filters.sortBy === "price-asc") {
          result.sort((a, b) => a.price - b.price);
        } else if (filters.sortBy === "price-desc") {
          result.sort((a, b) => b.price - a.price);
        } else if (filters.sortBy === "rating") {
          result.sort((a, b) => b.rating - a.rating);
        }

        // Đưa sản phẩm thuộc danh mục đã chọn lên đầu
        if (filters.categoryId) {
          const matched = result.filter(
            (p) => p.categoryId === filters.categoryId
          );
          const unmatched = result.filter(
            (p) => p.categoryId !== filters.categoryId
          );
          result = [...matched, ...unmatched];
        }
        setFilteredProducts(result);
      })
      .finally(() => setLoadingProducts(false));
  }, [filters, lang]);
 
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
 
  // ─── Notifications ─────────────────────────────────────
  const [notifications, setNotifications] = useState([]);

  const unreadNotificationsCount = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  );

  const markNotificationsAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
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
    notifications,
    unreadNotificationsCount,
    markNotificationsAsRead,
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
    lang,
    setLang: changeLang,
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