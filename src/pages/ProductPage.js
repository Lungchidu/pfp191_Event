import { useState, useEffect, useCallback } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, ShoppingCart, Star, Send, AlertCircle, CheckCircle,
} from "lucide-react";
import { PRODUCTS, formatPrice } from "../data/mockData";
import { useApp } from "../context/AppContext";
import { API_BASE, getStoredUsername, isLoggedIn } from "../config/auth";
import { translateProduct, translations } from "../data/i18n";
import "../styles/product.css";

// ── Helper gọi API ─────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const username = getStoredUsername();
  const token = localStorage.getItem("token");

  // Tách body và headers ra khỏi opts, merge headers đúng cách
  const { headers: extraHeaders = {}, ...restOpts } = opts;

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...restOpts,
    headers: {
      "Content-Type": "application/json",
      ...(username ? { "X-Username": username } : {}),
      ...(token ? { "Authorization": `Bearer ${token}` } : {}),
      ...extraHeaders,
    },
  });
  const text = await res.text();
  try { return { ok: res.ok, data: JSON.parse(text) }; }
  catch { return { ok: false, data: { message: text } }; }
}

// ── Star Rating Component ─────────────────────────────────────
function StarRating({ value, onChange, readOnly = false }) {
  const [hover, setHover] = useState(0);
  return (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          className={`star-btn ${(hover || value) >= star ? "active" : ""}`}
          onClick={() => !readOnly && onChange && onChange(star)}
          onMouseEnter={() => !readOnly && setHover(star)}
          onMouseLeave={() => !readOnly && setHover(0)}
          disabled={readOnly}
          aria-label={`${star} stars`}
        >
          ★
        </button>
      ))}
    </div>
  );
}

// ── Main ProductPage ─────────────────────────────────────────────
export default function ProductPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart, lang } = useApp();
  const t = translations[lang] || translations.vi;

  // ── Product state ─────────────────────────────────
  const [productData, setProductData] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ── Order state ───────────────────────────────────
  const [quantity, setQuantity] = useState(1);
  const [days, setDays] = useState(1);

  // ── Review state ─────────────────────────────────
  const [reviews, setReviews] = useState([]);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [reviewMsg, setReviewMsg] = useState({ type: "", text: "" });

  // ── Load product từ API rồi fallback mockData ────
  const loadProduct = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { ok, data } = await apiFetch(`/api/products/${id}`);
      if (ok && data.success) {
        setProductData(data.product);
        setRelated(data.related || []);
      } else {
        // Fallback: tìm trong mockData
        const found = PRODUCTS.find((p) => p.id === Number(id));
        if (found) {
          setProductData(found);
          setRelated(
            PRODUCTS.filter(
              (p) => p.categoryId === found.categoryId && p.id !== found.id
            ).slice(0, 4)
          );
        } else {
          setError(lang === "en" ? "Product not found." : "Không tìm thấy sản phẩm.");
        }
      }
    } catch {
      // Backend chưa chạy → fallback mockData
      const found = PRODUCTS.find((p) => p.id === Number(id));
      if (found) {
        setProductData(found);
        setRelated(
          PRODUCTS.filter(
            (p) => p.categoryId === found.categoryId && p.id !== found.id
          ).slice(0, 4)
        );
      } else {
        setError(lang === "en" ? "Product not found." : "Không tìm thấy sản phẩm.");
      }
    } finally {
      setLoading(false);
    }
  }, [id, lang]);

  // ── Load reviews ─────────────────────────────────
  const loadReviews = useCallback(async () => {
    setReviewsLoading(true);
    try {
      const { ok, data } = await apiFetch(`/api/products/${id}/reviews`);
      if (ok && data.success) {
        setReviews(data.reviews || []);
      }
    } catch { /* backend chưa chạy */ }
    finally { setReviewsLoading(false); }
  }, [id]);

  useEffect(() => {
    window.scrollTo(0, 0);
    loadProduct();
    loadReviews();
  }, [id, loadProduct, loadReviews]);

  // ── Submit review ─────────────────────────────────
  async function handleSubmitReview(e) {
    e.preventDefault();
    if (!isLoggedIn()) {
      navigate("/auth?mode=login");
      return;
    }
    if (!newComment.trim()) {
      setReviewMsg({
        type: "error",
        text: lang === "en" ? "Please enter a comment!" : "Vui lòng nhập nội dung bình luận!"
      });
      return;
    }
    setSubmitting(true);
    setReviewMsg({ type: "", text: "" });

    try {
      const { ok, data } = await apiFetch(`/api/products/${id}/reviews`, {
        method: "POST",
        body: JSON.stringify({ rating: newRating, comment: newComment.trim() }),
      });
      setSubmitting(false);

      if (ok && data.success) {
        setReviewMsg({
          type: "success",
          text: lang === "en" ? "Review posted successfully!" : data.message
        });
        setNewComment("");
        setNewRating(5);
        loadReviews();
        loadProduct(); // Tải lại thông tin sản phẩm (để cập nhật rating trung bình mới nhất)
      } else {
        setReviewMsg({
          type: "error",
          text: lang === "en" ? (data.message || "Failed to submit review!") : (data.message || "Lỗi khi gửi bình luận!")
        });
      }
    } catch (err) {
      // Backend offline → kiểm tra localStorage
      setSubmitting(false);
      const localRaw = JSON.parse(localStorage.getItem("local_orders") || "[]");
      
      // Tìm xem có đơn nào chứa sản phẩm này mà trạng thái đã giao (completed) chưa
      const hasCompletedOrder = localRaw.some(order => 
        order.status === "completed" && 
        (order.items || []).some(item => String(item.product_id || item.id) === String(id) || item.product_name === productData?.name)
      );

      if (hasCompletedOrder) {
        // Mô phỏng lưu comment cục bộ
        const fakeReview = {
          id: `fake-rv-${Date.now()}`,
          username: getStoredUsername() || (lang === "en" ? "Customer" : "Khách hàng"),
          rating: newRating,
          comment: newComment.trim(),
          createdAt: new Date().toLocaleDateString(lang === "en" ? "en-US" : "vi-VN"),
          productImage: productData?.image,
        };
        setReviews(prev => [fakeReview, ...prev]);
        setReviewMsg({
          type: "success",
          text: lang === "en" ? "Review submitted! (Offline mode)" : "Đã gửi bình luận! (Chế độ offline)"
        });
        setNewComment("");
        setNewRating(5);
      } else {
        setReviewMsg({
          type: "error",
          text: lang === "en"
            ? "You must complete delivery (status 'completed') for this equipment to post a review!"
            : "Bạn cần phải nhận được hàng (đơn hàng đã giao thành công) mới có thể bình luận!"
        });
      }
    }
  }

  // ── Render states ─────────────────────────────────
  if (loading) {
    return (
      <div className="product-page container product-page--loading">
        <div className="product-skeleton" />
      </div>
    );
  }

  const translatedProduct = translateProduct(productData, lang);

  if (error || !translatedProduct) {
    return (
      <div className="product-page container product-page--error">
        <AlertCircle size={48} color="#e11d48" />
        <p>{error || (lang === "en" ? "Product not found." : "Không tìm thấy sản phẩm.")}</p>
        <Link to="/" className="btn-primary">
          {lang === "en" ? "← Back to home" : "← Về trang chủ"}
        </Link>
      </div>
    );
  }

  const total = translatedProduct.price * quantity * days;
  const avgRating = translatedProduct.rating || 5.0;

  return (
    <div className="product-page">
      <div className="container">
        {/* Back button */}
        <Link to="/" className="product-page__back">
          <ArrowLeft size={18} /> {lang === "en" ? "Back" : "Quay lại"}
        </Link>

        {/* Product detail */}
        <div className="product-detail">
          <div className="product-detail__gallery">
            <img src={translatedProduct.image} alt={translatedProduct.name} />
            {translatedProduct.isFlash && (
              <span className="product-detail__flash">
                {lang === "en" ? "🔥 Flash Rental" : "🔥 Thuê gấp"}
              </span>
            )}
            {translatedProduct.discount > 0 && (
              <span className="product-detail__discount-badge">
                -{translatedProduct.discount}%
              </span>
            )}
          </div>

          <div className="product-detail__info">
            <h1>{translatedProduct.name}</h1>
            <p className="product-detail__rating">
              <Star size={16} fill="#d97706" stroke="#d97706" />
              <span className="rating-value">{avgRating}</span>
              <span className="rating-sep">·</span>
              {translatedProduct.location}
              <span className="rating-sep">·</span>
              {lang === "en"
                ? `Rented ${translatedProduct.sold} times`
                : `Đã thuê ${translatedProduct.sold} lần`}
              {reviews.length > 0 && (
                <a href="#reviews" className="reviews-link">
                  ({reviews.length} {lang === "en" ? "reviews" : "đánh giá"})
                </a>
              )}
            </p>

            <div className="product-detail__pricing">
              <span className="product-detail__price">
                {formatPrice(translatedProduct.price)}
              </span>
              <span className="product-detail__unit">
                /{lang === "en" ? "day" : "ngày"}
              </span>
              {translatedProduct.originalPrice > translatedProduct.price && (
                <span className="product-detail__original">
                  {formatPrice(translatedProduct.originalPrice)}
                </span>
              )}
            </div>

            <p className="product-detail__desc">{translatedProduct.description}</p>

            <ul className="product-detail__specs">
              {(translatedProduct.specs || []).map((spec) => (
                <li key={spec}>✓ {spec}</li>
              ))}
            </ul>

            {/* Form đặt hàng */}
            <div className="product-detail__form">
              <label>
                {lang === "en" ? "Quantity" : "Số lượng"}
                <input
                  type="number"
                  min={1}
                  max={translatedProduct.stock}
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(Math.max(1, Number(e.target.value) || 1))
                  }
                />
              </label>
              <label>
                {lang === "en" ? "Rental days" : "Số ngày thuê"}
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
              {lang === "en" ? "Total estimation: " : "Tạm tính: "}
              <strong>{formatPrice(total)}</strong>
            </p>

            <div className="product-detail__actions">
              <button
                type="button"
                className="btn-primary"
                onClick={() => addToCart(translatedProduct, quantity, days)}
              >
                <ShoppingCart size={18} />
                {lang === "en" ? "Add to cart" : "Thêm vào giỏ thuê"}
              </button>
              <Link to="/cart" className="btn-secondary">
                {lang === "en" ? "View cart" : "Xem giỏ thuê"}
              </Link>
            </div>

            <p className="product-detail__stock">
              {lang === "en" ? "Only " : "Còn "}
              <strong>
                {Math.max(0, (translatedProduct.stock || 0) - (translatedProduct.sold || 0))}
              </strong>{" "}
              {lang === "en" ? "units available" : "suất có sẵn"}
            </p>
          </div>
        </div>

        {/* Sản phẩm liên quan */}
        {related.length > 0 && (
          <section className="product-related">
            <h2>{lang === "en" ? "Related products" : "Sản phẩm liên quan"}</h2>
            <div className="product-related__grid">
              {related.map((rp) => {
                const rpTrans = translateProduct(rp, lang);
                return (
                  <button
                    key={rpTrans.id}
                    type="button"
                    className="product-related__card"
                    onClick={() => navigate(`/product/${rpTrans.id}`)}
                  >
                    <img src={rpTrans.image} alt={rpTrans.name} />
                    <span>{rpTrans.name}</span>
                    <strong>
                      {formatPrice(rpTrans.price)}/{lang === "en" ? "day" : "ngày"}
                    </strong>
                  </button>
                );
              })}
            </div>
          </section>
        )}

        {/* ── Khu vực bình luận & đánh giá ── */}
        <section className="reviews-section" id="reviews">
          <h2 className="reviews-section__title">
            {lang === "en" ? "Reviews & Comments" : "Đánh giá &amp; Bình luận"}
            {reviews.length > 0 && (
              <span className="reviews-count">
                ({reviews.length} {lang === "en" ? "reviews" : "đánh giá"})
              </span>
            )}
          </h2>

          {/* Form gửi đánh giá */}
          <div className="review-form-card">
            <h3>{lang === "en" ? "Write your review" : "Viết đánh giá của bạn"}</h3>
            <p className="review-form-notice">
              <AlertCircle size={14} />
              {lang === "en"
                ? "Only customers who received the equipment (status 'completed') can leave a review."
                : "Chỉ khách hàng đã nhận được thiết bị (đơn hàng đã giao thành công) mới có thể bình luận."}
            </p>

            {!isLoggedIn() ? (
              <div className="review-login-prompt">
                <p>{lang === "en" ? "You must sign in to leave a review." : "Bạn cần đăng nhập để gửi đánh giá."}</p>
                <Link to="/auth?mode=login" className="btn-primary" style={{ display: "inline-flex" }}>
                  {lang === "en" ? "Sign in now" : "Đăng nhập ngay"}
                </Link>
              </div>
            ) : (
              <form className="review-form" onSubmit={handleSubmitReview}>
                <div className="review-form__rating-row">
                  <span>{lang === "en" ? "Rating:" : "Xếp hạng:"}</span>
                  <StarRating value={newRating} onChange={setNewRating} />
                  <span className="rating-label">
                    {newRating} / 5 {lang === "en" ? "stars" : "sao"}
                  </span>
                </div>
                <textarea
                  className="review-form__textarea"
                  placeholder={
                    lang === "en"
                      ? "Share your equipment rental experience..."
                      : "Chia sẻ trải nghiệm thuê thiết bị của bạn..."
                  }
                  rows={4}
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  maxLength={1000}
                />
                <div className="review-form__footer">
                  <span className="char-count">{newComment.length}/1000</span>
                  <button
                    type="submit"
                    className="btn-primary review-submit-btn"
                    disabled={submitting}
                  >
                    <Send size={16} />
                    {submitting
                      ? (lang === "en" ? "Sending..." : "Đang gửi...")
                      : (lang === "en" ? "Submit review" : "Gửi đánh giá")}
                  </button>
                </div>
                {reviewMsg.text && (
                  <div
                    className={`review-msg ${reviewMsg.type === "success" ? "review-msg--success" : "review-msg--error"}`}
                  >
                    {reviewMsg.type === "success" ? (
                      <CheckCircle size={16} />
                    ) : (
                      <AlertCircle size={16} />
                    )}
                    {reviewMsg.text}
                  </div>
                )}
              </form>
            )}
          </div>

          {/* Danh sách đánh giá */}
          <div className="reviews-list">
            {reviewsLoading ? (
              <p className="reviews-empty">
                {lang === "en" ? "Loading reviews..." : "Đang tải đánh giá..."}
              </p>
            ) : reviews.length === 0 ? (
              <p className="reviews-empty">
                {lang === "en"
                  ? "No reviews yet. Be the first to leave one!"
                  : "Chưa có đánh giá nào. Hãy là người đầu tiên nhận xét!"}
              </p>
            ) : (
              reviews.map((rv) => (
                <div key={rv.id} className="review-card">
                  <div className="review-card__header">
                    <div className="review-card__avatar">
                      {rv.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="review-card__meta">
                      <strong className="review-card__username">
                        {rv.username}
                      </strong>
                      <span className="review-card__date">{rv.createdAt}</span>
                    </div>
                    <div className="review-card__stars">
                      {[1, 2, 3, 4, 5].map((s) => (
                        <span
                          key={s}
                          className={s <= rv.rating ? "star-filled" : "star-empty"}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Ảnh sản phẩm kèm bình luận */}
                  {rv.productImage && (
                    <div className="review-card__product-img">
                      <img src={rv.productImage} alt="Product" />
                      <span className="review-card__verified">
                        <CheckCircle size={12} /> {lang === "en" ? "Rented" : "Đã thuê"}
                      </span>
                    </div>
                  )}

                  <p className="review-card__comment">{rv.comment}</p>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

