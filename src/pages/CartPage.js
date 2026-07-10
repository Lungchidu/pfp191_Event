import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Minus, Plus, Trash2 } from "lucide-react";
import { formatPrice } from "../data/mockData";
import { useApp } from "../context/AppContext";
import { isLoggedIn } from "../config/auth";
import { translations } from "../data/i18n";
import "../styles/cart.css";

export default function CartPage() {
  const navigate = useNavigate();
  const {
    cart,
    cartTotal,
    updateCartItem,
    removeFromCart,
    lang,
  } = useApp();
  const t = translations[lang] || translations.vi;

  const handleCheckout = () => {
    if (cart.length === 0) return;
    if (!isLoggedIn()) {
      navigate("/auth?mode=login");
      return;
    }
    navigate("/checkout");
  };

  return (
    <div className="cart-page">
      <div className="container">
        <Link to="/" className="cart-page__back">
          <ArrowLeft size={18} /> {t.continueRenting}
        </Link>

        <h1>{t.cartTitle} ({cart.length} {t.items})</h1>

        {cart.length === 0 ? (
          <div className="cart-empty">
            <p>{t.cartEmpty}</p>
            <Link to="/" className="btn-primary">
              {t.exploreEquipment}
            </Link>
          </div>
        ) : (
          <>
            <ul className="cart-list">
              {cart.map((item) => (
                <li key={item.id} className="cart-item">
                  <img src={item.image} alt={item.name} />
                  <div className="cart-item__info">
                    <h3>{item.name}</h3>
                    <p>{item.location}</p>
                    <p className="cart-item__price">
                      {formatPrice(item.price)}/{t.perDay}
                    </p>
                  </div>

                  <div className="cart-item__qty">
                    <button
                      type="button"
                      onClick={() =>
                        updateCartItem(item.id, {
                          quantity: item.quantity - 1,
                        })
                      }
                      aria-label={lang === "en" ? "Decrease quantity" : "Giảm số lượng"}
                    >
                      <Minus size={16} />
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      type="button"
                      onClick={() =>
                        updateCartItem(item.id, {
                          quantity: item.quantity + 1,
                        })
                      }
                      aria-label={lang === "en" ? "Increase quantity" : "Tăng số lượng"}
                    >
                      <Plus size={16} />
                    </button>
                  </div>

                  <div className="cart-item__days">
                    <label>
                      {t.days}
                      <input
                        type="number"
                        min={1}
                        value={item.days}
                        onChange={(e) =>
                          updateCartItem(item.id, {
                            days: Math.max(
                              1,
                              Number(e.target.value) || 1
                            ),
                          })
                        }
                      />
                    </label>
                  </div>

                  <p className="cart-item__subtotal">
                    {formatPrice(
                      item.price * item.quantity * item.days
                    )}
                  </p>

                  <button
                    type="button"
                    className="cart-item__remove"
                    onClick={() => removeFromCart(item.id)}
                    aria-label={lang === "en" ? "Remove" : "Xóa"}
                  >
                    <Trash2 size={18} />
                  </button>
                </li>
              ))}
            </ul>

            <div className="cart-summary">
              <div>
                <span>{t.totalLabel}</span>
                <strong>{formatPrice(cartTotal)}</strong>
              </div>
              <button
                type="button"
                className="btn-primary"
                onClick={handleCheckout}
              >
                {t.checkoutBtn}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
