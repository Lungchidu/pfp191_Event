import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, CreditCard, ShieldCheck, User } from "lucide-react";
import { formatPrice } from "../data/mockData";
import { useApp } from "../context/AppContext";
import { isLoggedIn } from "../config/auth";
import { checkoutCart, fetchProfile, updateProfile } from "../services/shopApi";
import { translations } from "../data/i18n";
import "../styles/checkout.css";

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { cart, cartTotal, showToast, clearCart, lang } = useApp();
  const t = translations[lang] || translations.vi;
  const [paymentMethod, setPaymentMethod] = useState("cod");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);

  // Profile details state
  const [fullName, setFullName] = useState("");
  const [birthYear, setBirthYear] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");

  useEffect(() => {
    if (isLoggedIn()) {
      fetchProfile()
        .then((profile) => {
          if (profile) {
            setFullName(profile.fullName || "");
            setBirthYear(profile.birthYear || "");
            setPhone(profile.phone || "");
            setAddress(profile.address || "");
          }
        })
        .catch((err) => {
          console.error("Failed to load profile for checkout:", err);
          const localProfile = JSON.parse(localStorage.getItem("local_profile") || "{}");
          setFullName(localProfile.fullName || "");
          setBirthYear(localProfile.birthYear || "");
          setPhone(localProfile.phone || "");
          setAddress(localProfile.address || "");
        });
    }
  }, []);

  if (!isLoggedIn()) {
    return (
      <div className="checkout-page">
        <div className="container checkout-empty">
          <p>{t.loginRequired}</p>
          <Link to="/auth?mode=login" className="btn-primary">
            {t.loginBtn}
          </Link>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="checkout-page">
        <div className="container checkout-empty">
          <p>{t.cartEmptyMsg}</p>
          <Link to="/" className="btn-primary">
            {t.exploreEquipment}
          </Link>
        </div>
      </div>
    );
  }

  const handlePlaceOrder = async () => {
    if (cart.length === 0) return;
    if (!address || !address.trim()) {
      showToast(lang === "en" ? "Delivery address is required!" : "Vui lòng nhập địa chỉ giao hàng!");
      return;
    }
    setLoading(true);
    try {
      // Tự động lưu thông tin cá nhân/địa chỉ lên backend
      await updateProfile({ fullName, birthYear: birthYear ? parseInt(birthYear, 10) : 0, phone, address });
      const result = await checkoutCart(cart, note, { fullName, birthYear, phone, address });
      clearCart();
      showToast(result.message || (lang === "en" ? "Order placed successfully!" : "Đặt thuê thành công!"));
      navigate("/", { replace: true });
    } catch (err) {
      // Lưu tạm thông tin cá nhân vào local storage khi offline
      localStorage.setItem("local_profile", JSON.stringify({ fullName, birthYear, phone, address }));

      // Nếu backend không chạy (offline mode) → lưu đơn vào localStorage
      const isOffline =
        err.message?.includes("fetch") ||
        err.message?.includes("server") ||
        err.message?.includes("Failed") ||
        err.message?.includes("NetworkError") ||
        err.message?.includes("python") ||
        err.message?.includes("Python");

      if (isOffline) {
        const orderId = `EVR-${Date.now().toString().slice(-6)}`;
        const localOrder = {
          id: orderId,
          items: cart.map((i) => ({ product_name: i.name, price: i.price, quantity: i.quantity, days: i.days })),
          total: cartTotal,
          status: "completed",
          note: note,
          created_at: new Date().toLocaleString("sv-SE"),
        };
        const existing = JSON.parse(localStorage.getItem("local_orders") || "[]");
        localStorage.setItem("local_orders", JSON.stringify([localOrder, ...existing]));
        clearCart();
        showToast(lang === "en" ? "Order placed! (Offline mode)" : "Đặt thuê thành công! (Chế độ offline)");
        navigate("/", { replace: true });
      } else {
        showToast(err.message || (lang === "en" ? "Could not place order. Please try again." : "Không thể đặt thuê. Vui lòng thử lại."));
      }
    } finally {
      setLoading(false);
    }
  };

  const paymentOptions = [
    { id: "cod", label: t.paymentCOD },
    { id: "transfer", label: t.paymentTransfer },
    { id: "momo", label: t.paymentMomo },
  ];

  return (
    <div className="checkout-page">
      <header className="checkout-header">
        <div className="container checkout-header__inner">
          <Link to="/cart" className="checkout-header__back">
            <ArrowLeft size={18} /> {t.backToCart}
          </Link>
          <h1>{t.checkoutTitle}</h1>
        </div>
      </header>

      <div className="container checkout-layout">
        <div className="checkout-main">
          <section className="checkout-card">
            <h2>
              <MapPin size={20} /> {t.deliveryAddress}
            </h2>
            <p className="checkout-address" style={{ marginBottom: "16px", color: "#0f766e", fontWeight: 600 }}>
              {cart[0]?.location || "Hồ Chí Minh"} — {t.deliveryNote}
            </p>
            
            <div className="checkout-profile-fields" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginTop: "12px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <label style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>{t.fullNameLabel}</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder={t.fullNameLabel}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  required
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <label style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>{t.birthYearLabel}</label>
                <input
                  type="number"
                  value={birthYear}
                  onChange={(e) => setBirthYear(e.target.value)}
                  placeholder={t.birthYearLabel}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", gridColumn: "span 2" }}>
                <label style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>{t.phoneLabel}</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder={t.phoneLabel}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  required
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", gridColumn: "span 2" }}>
                <label style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>{t.addressLabel}</label>
                <textarea
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder={t.addressLabel}
                  rows={2}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1", fontFamily: "inherit" }}
                  required
                />
              </div>
            </div>
          </section>

          <section className="checkout-card">
            <h2>{t.rentalItems} ({cart.length})</h2>
            <ul className="checkout-items">
              {cart.map((item) => (
                <li key={item.id} className="checkout-item">
                  <img src={item.image} alt={item.name} />
                  <div>
                    <strong>{item.name}</strong>
                    <p>
                      {formatPrice(item.price)}/{t.perDay} × {item.quantity} × {item.days}{" "}
                      {t.perDay}
                    </p>
                  </div>
                  <span>{formatPrice(item.price * item.quantity * item.days)}</span>
                </li>
              ))}
            </ul>
            <label className="checkout-note">
              {t.orderNote}
              <textarea
                rows={2}
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder={t.orderNotePlaceholder}
              />
            </label>
          </section>

          <section className="checkout-card">
            <h2>
              <CreditCard size={20} /> {t.paymentMethod}
            </h2>
            <div className="checkout-payments">
              {paymentOptions.map((opt) => (
                <label
                  key={opt.id}
                  className={`checkout-payment ${
                    paymentMethod === opt.id ? "selected" : ""
                  }`}
                >
                  <input
                    type="radio"
                    name="payment"
                    value={opt.id}
                    checked={paymentMethod === opt.id}
                    onChange={() => setPaymentMethod(opt.id)}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </section>
        </div>

        <aside className="checkout-summary">
          <h2>{t.orderSummary}</h2>
          <div className="checkout-summary__row">
            <span>{t.subtotal}</span>
            <span>{formatPrice(cartTotal)}</span>
          </div>
          <div className="checkout-summary__row">
            <span>{t.shippingFee}</span>
            <span className="checkout-free">{t.freeShipping}</span>
          </div>
          <div className="checkout-summary__total">
            <span>{t.totalPayment}</span>
            <strong>{formatPrice(cartTotal)}</strong>
          </div>
          <button
            type="button"
            className="btn-primary checkout-submit"
            onClick={handlePlaceOrder}
            disabled={loading}
          >
            {loading ? t.processing : t.placeOrder}
          </button>
          <p className="checkout-secure">
            <ShieldCheck size={16} /> {t.secureTx}
          </p>
        </aside>
      </div>
    </div>
  );
}
