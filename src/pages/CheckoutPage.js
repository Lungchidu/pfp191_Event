import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, CreditCard, ShieldCheck } from "lucide-react";
import { formatPrice } from "../data/mockData";
import { useApp } from "../context/AppContext";
import { isLoggedIn } from "../config/auth";
import { checkoutCart } from "../services/shopApi";
import "../styles/checkout.css";

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { cart, cartTotal, showToast, clearCart } = useApp();
  const [paymentMethod, setPaymentMethod] = useState("cod");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isLoggedIn()) {
    return (
      <div className="checkout-page">
        <div className="container checkout-empty">
          <p>Bạn cần đăng nhập để thanh toán.</p>
          <Link to="/auth?mode=login" className="btn-primary">
            Đăng nhập
          </Link>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="checkout-page">
        <div className="container checkout-empty">
          <p>Giỏ thuê đang trống.</p>
          <Link to="/" className="btn-primary">
            Khám phá thiết bị
          </Link>
        </div>
      </div>
    );
  }

  const handlePlaceOrder = async () => {
    if (cart.length === 0) return;
    setLoading(true);
    try {
      const result = await checkoutCart(cart, note);
      clearCart();
      showToast(result.message || "Đặt thuê thành công!");
      navigate("/", { replace: true });
    } catch (err) {
      showToast(err.message || "Không thể đặt thuê. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-page">
      <header className="checkout-header">
        <div className="container checkout-header__inner">
          <Link to="/cart" className="checkout-header__back">
            <ArrowLeft size={18} /> Quay lại giỏ hàng
          </Link>
          <h1>Thanh toán</h1>
        </div>
      </header>

      <div className="container checkout-layout">
        <div className="checkout-main">
          <section className="checkout-card">
            <h2>
              <MapPin size={20} /> Địa điểm nhận thiết bị
            </h2>
            <p className="checkout-address">
              {cart[0]?.location || "Hồ Chí Minh"} — nhân viên sẽ liên hệ xác nhận
              địa chỉ giao/lắp đặt sau khi đặt thuê.
            </p>
          </section>

          <section className="checkout-card">
            <h2>Sản phẩm thuê ({cart.length})</h2>
            <ul className="checkout-items">
              {cart.map((item) => (
                <li key={item.id} className="checkout-item">
                  <img src={item.image} alt={item.name} />
                  <div>
                    <strong>{item.name}</strong>
                    <p>
                      {formatPrice(item.price)}/ngày × {item.quantity} × {item.days}{" "}
                      ngày
                    </p>
                  </div>
                  <span>{formatPrice(item.price * item.quantity * item.days)}</span>
                </li>
              ))}
            </ul>
            <label className="checkout-note">
              Ghi chú
              <textarea
                rows={2}
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Yêu cầu lắp đặt, khung giờ giao..."
              />
            </label>
          </section>

          <section className="checkout-card">
            <h2>
              <CreditCard size={20} /> Phương thức thanh toán
            </h2>
            <div className="checkout-payments">
              {[
                { id: "cod", label: "Thanh toán khi nhận thiết bị" },
                { id: "transfer", label: "Chuyển khoản ngân hàng" },
                { id: "momo", label: "Ví MoMo" },
              ].map((opt) => (
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
          <h2>Tổng đơn thuê</h2>
          <div className="checkout-summary__row">
            <span>Tạm tính</span>
            <span>{formatPrice(cartTotal)}</span>
          </div>
          <div className="checkout-summary__row">
            <span>Phí vận chuyển</span>
            <span className="checkout-free">Miễn phí</span>
          </div>
          <div className="checkout-summary__total">
            <span>Tổng thanh toán</span>
            <strong>{formatPrice(cartTotal)}</strong>
          </div>
          <button
            type="button"
            className="btn-primary checkout-submit"
            onClick={handlePlaceOrder}
            disabled={loading}
          >
            {loading ? "Đang xử lý..." : "Đặt thuê"}
          </button>
          <p className="checkout-secure">
            <ShieldCheck size={16} /> Giao dịch an toàn
          </p>
        </aside>
      </div>
    </div>
  );
}
