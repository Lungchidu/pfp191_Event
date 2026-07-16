import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { User, History, ArrowLeft, Save, ShoppingBag, Clock, FileText } from "lucide-react";
import { useApp } from "../context/AppContext";
import { isLoggedIn, getUsername } from "../config/auth";
import { fetchProfile, updateProfile, fetchOrders } from "../services/shopApi";
import { translations } from "../data/i18n";
import { formatPrice } from "../data/mockData";
import "./AccountPage.css";

export default function AccountPage() {
  const navigate = useNavigate();
  const { lang, showToast } = useApp();
  const t = translations[lang] || translations.vi;
  const [searchParams, setSearchParams] = useSearchParams();
  
  const activeTab = searchParams.get("tab") === "history" ? "history" : "profile";

  const [username, setUsername] = useState(() => getUsername());
  const [fullName, setFullName] = useState("");
  const [birthYear, setBirthYear] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [saving, setSaving] = useState(false);

  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(false);

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate("/auth?mode=login");
      return;
    }

    // Load Profile
    fetchProfile()
      .then((profile) => {
        if (profile) {
          setUsername(profile.username || getUsername());
          setFullName(profile.fullName || "");
          setBirthYear(profile.birthYear || "");
          setPhone(profile.phone || "");
          setAddress(profile.address || "");
        }
      })
      .catch((err) => {
        console.error("Failed to load user profile:", err);
        const localProfile = JSON.parse(localStorage.getItem("local_profile") || "{}");
        setFullName(localProfile.fullName || "");
        setBirthYear(localProfile.birthYear || "");
        setPhone(localProfile.phone || "");
        setAddress(localProfile.address || "");
      });

    // Load Orders
    setLoadingOrders(true);
    fetchOrders()
      .then((apiOrders) => {
        if (apiOrders) {
          setOrders(apiOrders);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch order history:", err);
        // Fallback to offline local storage orders
        const localRaw = JSON.parse(localStorage.getItem("local_orders") || "[]");
        setOrders(localRaw);
      })
      .finally(() => {
        setLoadingOrders(false);
      });
  }, [navigate]);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateProfile({
        fullName,
        birthYear: birthYear ? parseInt(birthYear, 10) : 0,
        phone,
        address
      });
      localStorage.setItem("local_profile", JSON.stringify({ fullName, birthYear, phone, address }));
      showToast(t.saveSuccess);
    } catch (err) {
      localStorage.setItem("local_profile", JSON.stringify({ fullName, birthYear, phone, address }));
      showToast(t.saveSuccess + " (Offline Mode)");
    } finally {
      setSaving(false);
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "pending": return t.statusPending;
      case "confirmed": return t.statusConfirmed;
      case "shipping": return t.statusShipping;
      case "completed": return t.statusCompleted;
      case "cancelled": return t.statusCancelled;
      default: return status;
    }
  };

  return (
    <div className="account-page">
      <header className="account-header">
        <div className="container account-header__inner">
          <button className="account-header__back" onClick={() => navigate("/")}>
            <ArrowLeft size={18} /> {t.backToHome}
          </button>
          <h1>{t.accountTitle}</h1>
        </div>
      </header>

      <div className="container account-layout">
        <aside className="account-sidebar">
          <div className="account-user-card">
            <div className="account-user-avatar">
              {username ? username.charAt(0).toUpperCase() : "U"}
            </div>
            <h3>{username}</h3>
          </div>
          <nav className="account-nav">
            <button
              className={`account-nav-btn ${activeTab === "profile" ? "active" : ""}`}
              onClick={() => setSearchParams({ tab: "profile" })}
            >
              <User size={18} /> {t.profileTab}
            </button>
            <button
              className={`account-nav-btn ${activeTab === "history" ? "active" : ""}`}
              onClick={() => setSearchParams({ tab: "history" })}
            >
              <History size={18} /> {t.historyTab}
            </button>
          </nav>
        </aside>

        <main className="account-main">
          {activeTab === "profile" && (
            <div className="account-card">
              <h2>{t.profileTab}</h2>
              <form onSubmit={handleSaveProfile} className="account-form">
                <div className="form-group">
                  <label>{t.usernameLabel}</label>
                  <input type="text" value={username} disabled style={{ backgroundColor: "#f1f5f9", cursor: "not-allowed", border: "1px solid #cbd5e1", borderRadius: "6px", padding: "10px", width: "100%", color: "#64748b" }} />
                </div>
                
                <div className="form-group">
                  <label>{t.fullNameLabel}</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder={t.fullNameLabel}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>{t.birthYearLabel}</label>
                  <input
                    type="number"
                    value={birthYear}
                    onChange={(e) => setBirthYear(e.target.value)}
                    placeholder={t.birthYearLabel}
                  />
                </div>

                <div className="form-group">
                  <label>{t.phoneLabel}</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder={t.phoneLabel}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>{t.addressLabel}</label>
                  <textarea
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder={t.addressLabel}
                    rows={3}
                    required
                  />
                </div>

                <button type="submit" className="btn-primary form-submit-btn" disabled={saving}>
                  <Save size={16} /> {saving ? t.saving : t.saveProfileBtn}
                </button>
              </form>
            </div>
          )}

          {activeTab === "history" && (
            <div className="account-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <h2>{t.historyTitle}</h2>
                <span style={{ fontSize: "12px", color: "#64748b" }}>{t.clickProductTip}</span>
              </div>

              {loadingOrders ? (
                <div className="account-loading">{t.loadingOrders || "Đang tải..."}</div>
              ) : orders.length === 0 ? (
                <div className="account-empty-state">
                  <ShoppingBag size={48} />
                  <p>{t.emptyHistory}</p>
                </div>
              ) : (
                <div className="order-history-list">
                  {orders.map((order) => (
                    <div key={order.id || order.db_id} className="order-history-card">
                      <div className="order-history-header">
                        <div>
                          <span className="order-history-id">{order.id}</span>
                          <span className="order-history-date">
                            <Clock size={12} /> {order.created_at}
                          </span>
                        </div>
                        <span className={`order-status-badge status-${order.status || "pending"}`}>
                          {getStatusLabel(order.status)}
                        </span>
                      </div>

                      <div className="order-history-body">
                        <h4 className="order-items-title">
                          <FileText size={14} /> {t.orderItemsLabel}
                        </h4>
                        <ul className="order-items-list">
                          {(order.items || []).map((item, idx) => (
                            <li key={idx} className="order-item-row">
                              {item.image && (
                                <img
                                  src={item.image}
                                  alt={item.product_name}
                                  className="order-item-thumb"
                                />
                              )}
                              <div className="order-item-details">
                                {item.id ? (
                                  <Link to={`/product/${item.id}`} className="order-item-name-link">
                                    {item.product_name}
                                  </Link>
                                ) : (
                                  <span className="order-item-name">{item.product_name}</span>
                                )}
                                <span className="order-item-qty">
                                  {formatPrice(item.price)} × {item.quantity} × {item.days} {t.perDay}
                                </span>
                              </div>
                              <span className="order-item-subtotal">
                                {formatPrice(item.price * item.quantity * item.days)}
                              </span>
                            </li>
                          ))}
                        </ul>

                        {order.note && (
                          <div className="order-note-block">
                            <strong>{t.orderNoteLabel}:</strong> {order.note}
                          </div>
                        )}
                      </div>

                      <div className="order-history-footer">
                        <span>{t.orderTotalLabel}</span>
                        <strong className="order-total-amount">{formatPrice(order.total)}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
