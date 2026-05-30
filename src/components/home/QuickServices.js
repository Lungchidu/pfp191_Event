import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";

export default function QuickServices() {
  const { ui, updateFilters } = useApp();
  const items = ui?.quickServices || [];

  if (items.length === 0) return null;

  return (
    <section className="container quick-services">
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          className="quick-services__item"
          onClick={() =>
            updateFilters(
              {
                query: item.filter.query || "",
                categoryId: item.filter.categoryId || null,
                location: item.filter.location || "",
                minRating: item.filter.minRating || 0,
                sortBy: item.filter.sortBy || "default",
                flashOnly: false,
              },
              { scrollToCatalog: true }
            )
          }
        >
          <div className="quick-services__icon">
            <DynamicIcon name={item.icon} size={24} />
          </div>
          <span>{item.label}</span>
        </button>
      ))}
    </section>
  );
}
