import { useApp } from "../../context/AppContext";

export default function PromoBanner({ t }) {
  const { showToast, updateFilters } = useApp();

  return (
    <section className="container promo-banner">
      <div className="promo-banner__text">
        <h3>{t.newUserPromo}</h3>
        <p>{t.newUserDesc}</p>
      </div>
      <button
        type="button"
        className="promo-banner__btn"
        onClick={() => {
          showToast("Đã áp dụng mã NEWUSER15 (demo)!");
          updateFilters(
            { sortBy: "price-asc" },
            { scrollToCatalog: true }
          );
        }}
      >
        {t.getNow}
      </button>
    </section>
  );
}
