import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, LogIn } from "lucide-react";
import { POPULAR_SEARCHES } from "../../data/mockData";
import { useApp } from "../../context/AppContext";
import { logout, getUsername } from "../../config/auth";

export default function Header({ t, lang, onLangChange }) {
  const { filters, search, cartCount } = useApp();
  const navigate = useNavigate();
  const [input, setInput] = useState(filters.query);
  const [username, setUsername] = useState(() => getUsername());

  useEffect(() => {
    setInput(filters.query);
  }, [filters.query]);

  // Sync username mỗi giây — bắt được cả khi DevTools xóa key trong cùng tab
  useEffect(() => {
    const syncUsername = () => setUsername(getUsername());
    const interval = setInterval(syncUsername, 1000);
    window.addEventListener("focus", syncUsername);
    return () => {
      clearInterval(interval);
      window.removeEventListener("focus", syncUsername);
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    search(input);
  };

  const handleLogout = () => {
    logout();
    setUsername("");
  };

  return (
    <>
      <div className="top-bar">
        <div className="container top-bar__inner">
          <div className="top-bar__links">
            <button type="button" className="top-bar__link-btn"
              onClick={() => alert("Kênh nhà cung cấp — sẽ kết nối backend sau.")}>
              {t.sellerCenter}
            </button>
            <button type="button" className="top-bar__link-btn"
              onClick={() => alert("Tải app EventRent — QR sẽ có khi publish.")}>
              {t.downloadApp}
            </button>
            <button type="button" className="top-bar__link-btn"
              onClick={() => alert("Hotline hỗ trợ: 1900-xxxx")}>
              {t.help}
            </button>
          </div>

          <div className="top-bar__social">
            <span>FB</span>
            <span>IG</span>
            <span>YT</span>

            <div className="top-bar__auth">
              {username ? (
                <>
                  <span className="top-bar__user">{t.hello}, {username}</span>
                  <span className="top-bar__divider">|</span>
                  <button type="button" className="top-bar__link-btn" onClick={handleLogout}>
                    {t.logout}
                  </button>
                </>
              ) : (
                <>
                  <button type="button" className="top-bar__link-btn"
                    onClick={() => navigate("/auth?mode=login")}>
                    {t.signIn || "Đăng nhập"}
                  </button>
                  <span className="top-bar__divider">|</span>
                  <button type="button" className="top-bar__link-btn"
                    onClick={() => navigate("/auth?mode=signup")}>
                    {t.signUp || "Đăng ký"}
                  </button>
                </>
              )}
              <span className="top-bar__divider">|</span>
              <button type="button" onClick={() => onLangChange("vi")}
                style={{ background: lang === "vi" ? "#334155" : "none", border: "none",
                  color: "inherit", cursor: "pointer", padding: "2px 6px", borderRadius: 4 }}>
                VI
              </button>
              <button type="button" onClick={() => onLangChange("en")}
                style={{ background: lang === "en" ? "#334155" : "none", border: "none",
                  color: "inherit", cursor: "pointer", padding: "2px 6px", borderRadius: 4 }}>
                EN
              </button>
            </div>
          </div>
        </div>
      </div>

      <header className="site-header">
        <div className="container">
          <div className="site-header__main">
            <Link to="/" className="brand">
              <div className="brand__logo">ER</div>
              <div>
                <h1 className="brand__name">EventRent</h1>
                <p className="brand__tagline">Equipment Rental & Logistics</p>
              </div>
            </Link>

            <div>
              <form className="search-bar" onSubmit={handleSubmit}>
                <input type="search" placeholder={t.searchPlaceholder}
                  aria-label={t.searchPlaceholder} value={input}
                  onChange={(e) => setInput(e.target.value)} />
                <button type="submit">{t.searchBtn}</button>
              </form>
              <div className="search-tags">
                {POPULAR_SEARCHES.map((term) => (
                  <span key={term} role="button" tabIndex={0}
                    onClick={() => search(term)}
                    onKeyDown={(e) => { if (e.key === "Enter") search(term); }}>
                    {term}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              {!username && (
                <button type="button" onClick={() => navigate("/auth?mode=login")}
                  style={{ display: "flex", alignItems: "center", gap: "6px",
                    background: "#0d9488", color: "#fff", border: "none",
                    borderRadius: "8px", padding: "8px 16px", fontWeight: 600,
                    fontSize: "14px", cursor: "pointer", whiteSpace: "nowrap" }}>
                  <LogIn size={16} />
                  Đăng nhập
                </button>
              )}
              <Link to="/cart" className="header-cart">
                <div className="header-cart__icon">
                  <ShoppingCart size={22} />
                  {cartCount > 0 && (
                    <span className="header-cart__badge">{cartCount}</span>
                  )}
                </div>
                <span>{t.cart}</span>
              </Link>
            </div>
          </div>
        </div>
      </header>
    </>
  );
}