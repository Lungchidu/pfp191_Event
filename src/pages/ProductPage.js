import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ShoppingCart, Star } from "lucide-react";
import { formatPrice } from "../utils/formatPrice";
import { fetchProductDetail } from "../services/shopApi";
import { useApp } from "../context/AppContext";
import "../styles/product.css";

export default function ProductPage() {
  const { id } = useParams();
  const { addToCart, goToProduct } = useApp();
  const [product, setProduct] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [days, setDays] = useState(1);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        const data = await fetchProductDetail(id);
        if (!cancelled) {
          setProduct(data.product);
          setRelated(data.related);
        }
      } catch {
        if (!cancelled) {
          setProduct(null);
          setRelated([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="product-page container">
        <p>Đang tải từ server Python...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-page container">
        <p>Không tìm thấy sản phẩm.</p>
        <Link to="/">← Về trang chủ</Link>
      </div>
    );
  }

  const total = product.price * quantity * days;

  return (
    <div className="product-page">
      <div className="container">
        <Link to="/" className="product-page__back">
          <ArrowLeft size={18} /> Quay lại
        </Link>

        <div className="product-detail">
          <div className="product-detail__gallery">
            <img src={product.image} alt={product.name} />
            {product.isFlash && (
              <span className="product-detail__flash">Thuê gấp</span>
            )}
          </div>

          <div className="product-detail__info">
            <h1>{product.name}</h1>
            <p className="product-detail__rating">
              <Star size={16} fill="#d97706" stroke="#d97706" />
              {product.rating} · {product.location} · Đã thuê{" "}
              {product.sold}
            </p>

            <div className="product-detail__pricing">
              <span className="product-detail__price">
                {formatPrice(product.price)}
              </span>
              <span className="product-detail__unit">/ngày</span>
              {product.originalPrice > product.price && (
                <span className="product-detail__original">
                  {formatPrice(product.originalPrice)}
                </span>
              )}
            </div>

            <p className="product-detail__desc">{product.description}</p>

            <ul className="product-detail__specs">
              {product.specs.map((spec) => (
                <li key={spec}>{spec}</li>
              ))}
            </ul>

            <div className="product-detail__form">
              <label>
                Số lượng
                <input
                  type="number"
                  min={1}
                  max={product.stock}
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(
                      Math.max(1, Number(e.target.value) || 1)
                    )
                  }
                />
              </label>
              <label>
                Số ngày thuê
                <input
                  type="number"
                  min={1}
                  value={days}
                  onChange={(e) =>
                    setDays(Math.max(1, Number(e.target.value) || 1))
                  }
                />
              </label>
            </div>

            <p className="product-detail__total">
              Tạm tính: <strong>{formatPrice(total)}</strong>
            </p>

            <div className="product-detail__actions">
              <button
                type="button"
                className="btn-primary"
                onClick={() => addToCart(product, quantity, days)}
              >
                <ShoppingCart size={18} />
                Thêm vào giỏ thuê
              </button>
              <Link to="/cart" className="btn-secondary">
                Xem giỏ thuê
              </Link>
            </div>

            <p className="product-detail__stock">
              Còn {product.stock - product.sold} suất
            </p>
          </div>
        </div>

        {related.length > 0 && (
          <section className="product-related">
            <h2>Sản phẩm liên quan</h2>
            <div className="product-related__grid">
              {related.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className="product-related__card"
                  onClick={() => goToProduct(p.id)}
                >
                  <img src={p.image} alt={p.name} />
                  <span>{p.name}</span>
                  <strong>{formatPrice(p.price)}/ngày</strong>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
