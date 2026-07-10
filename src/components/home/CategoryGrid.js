import { CATEGORIES } from "../../data/mockData";
import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";
import { translateCategory, translations } from "../../data/i18n";

export default function CategoryGrid({ title }) {
  const { filters, filterByCategory, clearFilters, lang } = useApp();
  const t = translations[lang] || translations.vi;

  return (
    <section className="container section-card">
      <div className="section-card__header">
        <h2 className="section-card__title">{title}</h2>
        <button
          type="button"
          className="section-card__link"
          onClick={clearFilters}
        >
          {lang === "en" ? "See all →" : "Xem tất cả →"}
        </button>
      </div>
      <div className="category-grid">
        {CATEGORIES.map((cat) => {
          const translatedCat = translateCategory(cat, lang);
          return (
            <button
              key={cat.id}
              type="button"
              className={`category-grid__item ${
                filters.categoryId === cat.id ? "active" : ""
              }`}
              onClick={() =>
                filterByCategory(
                  filters.categoryId === cat.id ? null : cat.id
                )
              }
            >
              <div className="category-grid__icon">
                <DynamicIcon name={cat.icon} />
              </div>
              <span>{translatedCat.name}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

