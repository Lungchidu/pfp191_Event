import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, LogIn, Truck, Bell } from "lucide-react";
import { POPULAR_SEARCHES } from "../../data/mockData";
import { useApp } from "../../context/AppContext";
import { logout, getUsername, isAdmin } from "../../config/auth";

export default function Header({ t, lang, onLangChange }) {
  const { filters, search, cartCount, notifications, unreadNotificationsCount, markNotificationsAsRead } = useApp();
  const navigate = useNavigate();
  const [input, setInput] = useState(filters.query);
  const [username, setUsername] = useState(() => getUsername());
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);

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
              onClick={() => alert("Hotline hỗ trợ: 1900-xxxx")}>
              {t.help}
            </button>
          </div>

          <div className="top-bar__social">
            <div className="top-bar__auth">
              {username ? (
                <>
                  <span className="top-bar__user">{t.hello}, {username}</span>
                  <span className="top-bar__divider">|</span>
                  <Link to="/account?tab=profile" className="top-bar__link-btn" style={{ textDecoration: "none", color: "inherit" }}>
                    {t.viewAccount}
                  </Link>
                  <span className="top-bar__divider">|</span>
                  <Link to="/account?tab=history" className="top-bar__link-btn" style={{ textDecoration: "none", color: "inherit" }}>
                    {t.viewHistory}
                  </Link>
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

            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              {!username && (
                <button type="button" onClick={() => navigate("/auth?mode=login")}
                  style={{ display: "flex", alignItems: "center", gap: "6px",
                    background: "#0d9488", color: "#fff", border: "none",
                    borderRadius: "8px", padding: "8px 16px", fontWeight: 600,
                    fontSize: "14px", cursor: "pointer", whiteSpace: "nowrap" }}>
                  <LogIn size={16} />
                  {t.loginBtn}
                </button>
              )}
              
              {username && isAdmin() && (
                <button type="button" onClick={() => navigate("/admin")}
                  style={{ display: "flex", alignItems: "center", gap: "6px",
                    background: "#0f766e", color: "#fff", border: "none",
                    borderRadius: "8px", padding: "8px 16px", fontWeight: 600,
                    fontSize: "14px", cursor: "pointer", whiteSpace: "nowrap" }}>
                  Admin
                </button>
              )}

              {/* Notification Center */}
              <div className="header-notification-container" style={{ position: "relative" }}>
                <button
                  type="button"
                  className="header-cart"
                  onClick={() => {
                    setShowNotifDropdown(!showNotifDropdown);
                    markNotificationsAsRead();
                  }}
                  style={{ background: "none", border: "none", color: "inherit", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "2px" }}
                >
                  <div className="header-cart__icon" style={{ position: "relative" }}>
                    <Bell size={22} />
                    {unreadNotificationsCount > 0 && (
                      <span className="header-cart__badge" style={{ background: "#ef4444" }}>{unreadNotificationsCount}</span>
                    )}
                  </div>
                  <span>{t.notifications}</span>
                </button>
                
                {showNotifDropdown && (
                  <div className="notif-dropdown" style={{
                    position: "absolute",
                    top: "100%",
                    right: 0,
                    width: "320px",
                    background: "#fff",
                    borderRadius: "8px",
                    boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
                    zIndex: 1000,
                    color: "#333",
                    padding: "12px",
                    marginTop: "8px",
                    border: "1px solid #e2e8f0",
                    textAlign: "left"
                  }}>
                    <h3 style={{ margin: "0 0 10px 0", fontSize: "15px", fontWeight: 700, borderBottom: "1px solid #f1f5f9", paddingBottom: "8px", color: "#0f766e" }}>
                      🔔 {t.latestNotif}
                    </h3>
                    {notifications.length === 0 ? (
                      <p style={{ margin: 0, fontSize: "13px", color: "#64748b", padding: "10px 0", textAlign: "center" }}>{t.noNotif}</p>
                    ) : (
                      <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "250px", overflowY: "auto" }}>
                        {notifications.map((notif) => (
                          <div
                            key={notif.id}
                            style={{
                              padding: "8px",
                              borderRadius: "6px",
                              background: notif.type === "warning" ? "#fffbeb" : "#f8fafc",
                              borderLeft: notif.type === "warning" ? "4px solid #f59e0b" : "4px solid #0d9488",
                              fontSize: "13px"
                            }}
                          >
                            <div style={{ fontWeight: 600, color: notif.type === "warning" ? "#b45309" : "#0f766e", marginBottom: "2px" }}>
                              {notif.title}
                            </div>
                            <div style={{ color: "#475569", lineHeight: "1.4" }}>{notif.message}</div>
                            <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "4px" }}>{notif.date}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <Link to="/order-tracking" className="header-cart">
                <div className="header-cart__icon">
                  <Truck size={22} />
                </div>
                <span>{t.tracking}</span>
              </Link>
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