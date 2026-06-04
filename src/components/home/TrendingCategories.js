import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";

export default function TrendingCategories({ title }) {
  const { ui, filterByKeyword } = useApp();
  const trending = ui?.trending || [];

  if (trending.length === 0) return null;

  return (
    <section className="container section-card">
      <h2 className="section-card__title">{title}</h2>
      <div className="trending-row">
        {trending.map((item) => (
          <button
            key={item.id}
            type="button"
            className="trending-card"
            onClick={() => filterByKeyword(item.keyword)}
          >
            <div className="trending-card__icon">
              <DynamicIcon name={item.icon} />
            </div>
            <h4>{item.name}</h4>
            <p>{item.count}</p>
          </button>
        ))}
      </div>
    </section>
  );
}
