import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart } from "lucide-react";
import { useApp } from "../../context/AppContext";
import { logout } from "../../config/auth";

export default function Header({ t, lang, onLangChange }) {
  const { ui, username, filters, search, cartCount } = useApp();
  const [input, setInput] = useState(filters.query);
  const popularSearches = ui?.popularSearches || [];

  useEffect(() => {
    setInput(filters.query);
  }, [filters.query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    search(input);
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <>
      <div className="top-bar">
        <div className="container top-bar__inner">
          <div className="top-bar__links">
            <button
              type="button"
              className="top-bar__link-btn"
              onClick={() =>
                alert("Kênh nhà cung cấp — sẽ kết nối backend sau.")
              }
            >
              {t.sellerCenter}
            </button>
            <button
              type="button"
              className="top-bar__link-btn"
              onClick={() =>
                alert("Tải app EventRent — QR sẽ có khi publish.")
              }
            >
              {t.downloadApp}
            </button>
            <button
              type="button"
              className="top-bar__link-btn"
              onClick={() => alert("Hotline hỗ trợ: 1900-xxxx")}
            >
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
                  <span className="top-bar__user">
                    {t.hello}, {username}
                  </span>
                  <span className="top-bar__divider">|</span>
                  <button
                    type="button"
                    className="top-bar__link-btn"
                    onClick={handleLogout}
                  >
                    {t.logout}
                  </button>
                </>
              ) : null}
              <span className="top-bar__divider">|</span>
              <button
                type="button"
                onClick={() => onLangChange("vi")}
                style={{
                  background: lang === "vi" ? "#334155" : "none",
                  border: "none",
                  color: "inherit",
                  cursor: "pointer",
                  padding: "2px 6px",
                  borderRadius: 4,
                }}
              >
                VI
              </button>
              <button
                type="button"
                onClick={() => onLangChange("en")}
                style={{
                  background: lang === "en" ? "#334155" : "none",
                  border: "none",
                  color: "inherit",
                  cursor: "pointer",
                  padding: "2px 6px",
                  borderRadius: 4,
                }}
              >
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
                <p className="brand__tagline">
                  Equipment Rental & Logistics
                </p>
              </div>
            </Link>

            <div>
              <form className="search-bar" onSubmit={handleSubmit}>
                <input
                  type="search"
                  placeholder={t.searchPlaceholder}
                  aria-label={t.searchPlaceholder}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <button type="submit">{t.searchBtn}</button>
              </form>
              <div className="search-tags">
                {popularSearches.map((term) => (
                  <span
                    key={term}
                    role="button"
                    tabIndex={0}
                    onClick={() => search(term)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") search(term);
                    }}
                  >
                    {term}
                  </span>
                ))}
              </div>
            </div>

            <Link to="/cart" className="header-cart">
              <div className="header-cart__icon">
                <ShoppingCart size={22} />
                {cartCount > 0 && (
                  <span className="header-cart__badge">
                    {cartCount}
                  </span>
                )}
              </div>
              <span>{t.cart}</span>
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}
