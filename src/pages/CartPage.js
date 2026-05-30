import { Link } from "react-router-dom";
import { ArrowLeft, Minus, Plus, Trash2 } from "lucide-react";
import { formatPrice } from "../data/mockData";
import { useApp } from "../context/AppContext";
import "../styles/cart.css";

export default function CartPage() {
  const {
    cart,
    cartTotal,
    updateCartItem,
    removeFromCart,
    showToast,
  } = useApp();

  const handleCheckout = () => {
    if (cart.length === 0) return;
    showToast(
      "Đặt thuê thành công (demo)! Backend sẽ xử lý đơn hàng sau."
    );
  };

  return (
    <div className="cart-page">
      <div className="container">
        <Link to="/" className="cart-page__back">
          <ArrowLeft size={18} /> Tiếp tục thuê thiết bị
        </Link>

        <h1>Giỏ thuê ({cart.length} mặt hàng)</h1>

        {cart.length === 0 ? (
          <div className="cart-empty">
            <p>Giỏ thuê đang trống.</p>
            <Link to="/" className="btn-primary">
              Khám phá thiết bị
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
                      {formatPrice(item.price)}/ngày
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
                      aria-label="Giảm số lượng"
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
                      aria-label="Tăng số lượng"
                    >
                      <Plus size={16} />
                    </button>
                  </div>

                  <div className="cart-item__days">
                    <label>
                      Ngày
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
                    aria-label="Xóa"
                  >
                    <Trash2 size={18} />
                  </button>
                </li>
              ))}
            </ul>

            <div className="cart-summary">
              <div>
                <span>Tổng cộng</span>
                <strong>{formatPrice(cartTotal)}</strong>
              </div>
              <button
                type="button"
                className="btn-primary"
                onClick={handleCheckout}
              >
                Đặt thuê ngay
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
