import { formatPrice } from "../../data/mockData";
import { useApp } from "../../context/AppContext";
import { translateProduct } from "../../data/i18n";

export default function ProductGrid({ t }) {
  const { filteredProducts, goToProduct, addToCart, filters, lang } =
    useApp();

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
        {filteredProducts.map((p) => {
          const product = translateProduct(p, lang);
          const isPriority =
            activeCategory &&
            (product.categoryId === activeCategory ||
              product.category_id === activeCategory);
          return (
            <article
              key={product.id}
              className={`product-card ${isPriority ? "priority-card" : ""}`}
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
                {isPriority && (
                  <div className="priority-badge">
                    {lang === "en" ? "✨ ⭐ The product you are looking for ⭐ ✨" : "✨ ⭐ Sản phẩm bạn đang tìm kiếm ⭐ ✨"}
                  </div>
                )}
              </div>
              <div className="product-card__body">
                <h3>{product.name}</h3>
              <p className="product-card__meta">
                {product.location} · ⭐ {product.rating}
              </p>
              <p className="product-card__price">
                {formatPrice(product.price)}
                <span>/{lang === "en" ? "day" : "ngày"}</span>
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
        );
      })}
      </div>
      {activeCategory && (
        <p className="product-grid__note">{t.clickForDetail}</p>
      )}
    </section>
  );
}

