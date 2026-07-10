import { TRENDING } from "../../data/mockData";
import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";
import { translateTrending } from "../../data/i18n";

export default function TrendingCategories({ title }) {
  const { filterByKeyword, lang } = useApp();

  return (
    <section className="container section-card">
      <div className="section-card__header">
        <h2 className="section-card__title">{title}</h2>
      </div>
      <div className="trending-row">
        {TRENDING.map((item) => {
          const translatedTrend = translateTrending(item, lang);
          return (
            <button
              key={item.id}
              type="button"
              className="trending-card"
              onClick={() => filterByKeyword(item.keyword)}
            >
              <div className="trending-card__icon">
                <DynamicIcon name={item.icon} />
              </div>
              <h4>{translatedTrend.name}</h4>
              <p>{item.count} {lang === "en" ? "products" : "sản phẩm"}</p>
            </button>
          );
        })}
      </div>
    </section>
  );
}

