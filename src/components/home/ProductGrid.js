import { formatPrice } from "../../utils/formatPrice";
import { useApp } from "../../context/AppContext";

export default function ProductGrid({ t }) {
  const { loading, filteredProducts, goToProduct, addToCart, filters } =
    useApp();

  if (loading) {
    return (
      <section className="container section-card product-empty">
        <p>Đang tải sản phẩm từ server Python...</p>
      </section>
    );
  }

  if (filteredProducts.length === 0) {
    return (
      <section className="container section-card product-empty">
        <p>{t.noResults}</p>
        <p className="product-empty__hint">{t.noResultsHint}</p>
      </section>
    );
  }

  const activeCategory = filters.categoryId;

  return (
    <section className="container section-card">
      <div className="product-grid">
        {filteredProducts.map((product) => (
          <article
            key={product.id}
            className="product-card"
            onClick={() => goToProduct(product.id)}
            onKeyDown={(e) => {
              if (e.key === "Enter") goToProduct(product.id);
            }}
            role="button"
            tabIndex={0}
          >
            <div className="product-card__img">
              <img src={product.image} alt={product.name} />
              {product.isFlash && (
                <span className="product-card__badge">Flash</span>
              )}
              {product.discount > 0 && (
                <span className="product-card__discount">
                  -{product.discount}%
                </span>
              )}
            </div>
            <div className="product-card__body">
              <h3>{product.name}</h3>
              <p className="product-card__meta">
                {product.location} · ⭐ {product.rating}
              </p>
              <p className="product-card__price">
                {formatPrice(product.price)}
                <span>/ngày</span>
              </p>
              <button
                type="button"
                className="product-card__btn"
                onClick={(e) => {
                  e.stopPropagation();
                  addToCart(product, 1, 1);
                }}
              >
                {t.addToCart}
              </button>
            </div>
          </article>
        ))}
      </div>
      {activeCategory && (
        <p className="product-grid__note">{t.clickForDetail}</p>
      )}
    </section>
  );
}
