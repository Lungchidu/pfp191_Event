import { FLASH_PRODUCTS, formatPrice } from "../../data/mockData";
import { useApp } from "../../context/AppContext";

export default function FlashRental({ title, seeMore }) {
  const { goToProduct, addToCart, updateFilters } = useApp();

  return (
    <section className="container section-card" id="flash">
      <div className="section-card__header">
        <h2 className="section-card__title">{title}</h2>
        <button
          type="button"
          className="section-card__link"
          onClick={() =>
            updateFilters(
              { flashOnly: true },
              { scrollToCatalog: true }
            )
          }
        >
          {seeMore} →
        </button>
      </div>
      <div className="flash-sale">
        {FLASH_PRODUCTS.map((product) => {
          const percent = Math.round(
            (product.sold / product.stock) * 100
          );
          return (
            <article
              key={product.id}
              className="flash-card"
              onClick={() => goToProduct(product.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter") goToProduct(product.id);
              }}
              role="button"
              tabIndex={0}
            >
              <div className="flash-card__img-wrap">
                <img src={product.image} alt={product.name} />
                <span className="flash-card__badge">
                  -{product.discount}%
                </span>
              </div>
              <p className="flash-card__name">{product.name}</p>
              <p className="flash-card__price">
                {formatPrice(product.price)}
              </p>
              <p className="flash-card__original">
                {formatPrice(product.originalPrice)}
              </p>
              <div className="flash-card__progress">
                <div
                  className="flash-card__progress-fill"
                  style={{ width: `${percent}%` }}
                />
                <span className="flash-card__progress-label">
                  Đã thuê {product.sold}
                </span>
              </div>
              <button
                type="button"
                className="flash-card__rent-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  addToCart(product, 1, 1);
                }}
              >
                Thuê ngay
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}
