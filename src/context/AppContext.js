import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { fetchCurrentUser } from "../config/auth";
import {
  fetchUiData,
  fetchProducts,
  fetchFlashProducts,
  fetchCategories,
  fetchLocations,
  fetchCart,
  addCartItem,
  updateCartItemApi,
  removeCartItemApi,
  checkoutCart,
} from "../services/shopApi";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [username, setUsername] = useState(null);
  const [ui, setUi] = useState(null);
  const [products, setProducts] = useState([]);
  const [flashProducts, setFlashProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
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

  const filteredProducts = products;

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

  const showToast = useCallback((message) => {
    setToast(message);
    const timer = setTimeout(() => setToast(null), 2800);
    return () => clearTimeout(timer);
  }, []);

  const initShop = useCallback(async () => {
    const user = await fetchCurrentUser();
    if (!user) {
      setLoading(false);
      return;
    }

    setUsername(user);

    try {
      setLoading(true);
      const [uiData, categoryList, locationList, flashList, cartItems] =
        await Promise.all([
          fetchUiData(),
          fetchCategories(),
          fetchLocations(),
          fetchFlashProducts(),
          fetchCart(),
        ]);

      setUi(uiData);
      setCategories(categoryList);
      setLocations(locationList);
      setFlashProducts(flashList);
      setCart(cartItems);
    } catch (err) {
      showToast(err.message || "Không tải được dữ liệu từ Python");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    initShop();
  }, [initShop]);

  useEffect(() => {
    if (!username) return;

    let cancelled = false;
    async function reload() {
      try {
        setLoading(true);
        const list = await fetchProducts(filters);
        if (!cancelled) setProducts(list);
      } catch (err) {
        if (!cancelled) showToast(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    reload();
    return () => {
      cancelled = true;
    };
  }, [filters, username, showToast]);

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
    (id) => products.find((p) => p.id === Number(id)),
    [products]
  );

  const addToCart = useCallback(
    async (product, quantity = 1, days = 1) => {
      try {
        const items = await addCartItem(product.id, quantity, days);
        setCart(items);
        showToast(`Đã thêm "${product.name}" vào giỏ thuê`);
      } catch (err) {
        showToast(err.message);
      }
    },
    [showToast]
  );

  const updateCartItem = useCallback(
    async (id, patch) => {
      try {
        const items = await updateCartItemApi(id, patch);
        setCart(items);
      } catch (err) {
        showToast(err.message);
      }
    },
    [showToast]
  );

  const removeFromCart = useCallback(
    async (id) => {
      try {
        const items = await removeCartItemApi(id);
        setCart(items);
        showToast("Đã xóa khỏi giỏ thuê");
      } catch (err) {
        showToast(err.message);
      }
    },
    [showToast]
  );

  const checkout = useCallback(async () => {
    try {
      const result = await checkoutCart();
      setCart([]);
      showToast(result.message);
    } catch (err) {
      showToast(err.message);
    }
  }, [showToast]);

  const value = {
    username,
    ui,
    products,
    flashProducts,
    categories,
    locations,
    loading,
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
    checkout,
    showToast,
    navigate,
    reloadShop: initShop,
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
