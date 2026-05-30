import { TRENDING } from "../../data/mockData";
import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";

export default function TrendingCategories({ title }) {
  const { filterByKeyword } = useApp();

  return (
    <section className="container section-card">
      <div className="section-card__header">
        <h2 className="section-card__title">{title}</h2>
      </div>
      <div className="trending-row">
        {TRENDING.map((item) => (
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
            <p>{item.count} sản phẩm</p>
          </button>
        ))}
      </div>
    </section>
  );
}
