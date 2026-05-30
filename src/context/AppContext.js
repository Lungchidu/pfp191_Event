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
import { filterProducts } from "../utils/filterProducts";

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

  const filters = useMemo(
    () => ({
      query: searchParams.get("q") || "",
      categoryId: searchParams.get("cat")
        ? Number(searchParams.get("cat"))
        : null,
      location: searchParams.get("loc") || "",
      minRating: Number(searchParams.get("rating") || 0),
      maxPrice: searchParams.get("max")
        ? Number(searchParams.get("max"))
        : null,
      flashOnly: searchParams.get("flash") === "1",
      sortBy: searchParams.get("sort") || "default",
      rentalDate: searchParams.get("date") || "",
    }),
    [searchParams]
  );

  const filteredProducts = useMemo(
    () => filterProducts(PRODUCTS, filters),
    [filters]
  );

  const cartCount = useMemo(
    () => cart.reduce((sum, item) => sum + item.quantity, 0),
    [cart]
  );

  const cartTotal = useMemo(
    () =>
      cart.reduce(
        (sum, item) => sum + item.price * item.quantity * item.days,
        0
      ),
    [cart]
  );

  useEffect(() => {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart]);

  const showToast = useCallback((message) => {
    setToast(message);
    const timer = setTimeout(() => setToast(null), 2800);
    return () => clearTimeout(timer);
  }, []);

  const updateFilters = useCallback(
    (patch, options = {}) => {
      const { scrollToCatalog = false } = options;
      const next = new URLSearchParams(searchParams);

      Object.entries(patch).forEach(([key, value]) => {
        const paramMap = {
          query: "q",
          categoryId: "cat",
          location: "loc",
          minRating: "rating",
          maxPrice: "max",
          flashOnly: "flash",
          sortBy: "sort",
          rentalDate: "date",
        };
        const param = paramMap[key] || key;

        if (
          value === null ||
          value === "" ||
          value === 0 ||
          value === false
        ) {
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
          document
            .getElementById("catalog")
            ?.scrollIntoView({ behavior: "smooth" });
        });
      }
    },
    [searchParams, setSearchParams]
  );

  const search = useCallback(
    (query) => {
      updateFilters({ query }, { scrollToCatalog: true });
    },
    [updateFilters]
  );

  const filterByCategory = useCallback(
    (categoryId) => {
      updateFilters(
        { categoryId: categoryId || null, query: "" },
        { scrollToCatalog: Boolean(categoryId) }
      );
    },
    [updateFilters]
  );

  const filterByKeyword = useCallback(
    (keyword) => {
      updateFilters({ query: keyword }, { scrollToCatalog: true });
    },
    [updateFilters]
  );

  const clearFilters = useCallback(() => {
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);

  const goToProduct = useCallback(
    (id) => navigate(`/product/${id}`),
    [navigate]
  );

  const getProduct = useCallback(
    (id) => PRODUCTS.find((p) => p.id === Number(id)),
    []
  );

  const addToCart = useCallback(
    (product, quantity = 1, days = 1) => {
      setCart((prev) => {
        const existing = prev.find((i) => i.id === product.id);
        if (existing) {
          return prev.map((i) =>
            i.id === product.id
              ? {
                  ...i,
                  quantity: i.quantity + quantity,
                  days: Math.max(i.days, days),
                }
              : i
          );
        }
        return [
          ...prev,
          {
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
            location: product.location,
            quantity,
            days,
          },
        ];
      });
      showToast(`Đã thêm "${product.name}" vào giỏ thuê`);
    },
    [showToast]
  );

  const updateCartItem = useCallback((id, patch) => {
    setCart((prev) =>
      prev
        .map((item) =>
          item.id === id ? { ...item, ...patch } : item
        )
        .filter((item) => item.quantity > 0)
    );
  }, []);

  const removeFromCart = useCallback((id) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
    showToast("Đã xóa khỏi giỏ thuê");
  }, [showToast]);

  const value = {
    filters,
    filteredProducts,
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
