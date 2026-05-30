import { QUICK_SERVICES } from "../../data/mockData";
import { DynamicIcon } from "../IconMap";
import { useApp } from "../../context/AppContext";

export default function QuickServices() {
  const { updateFilters } = useApp();

  return (
    <section className="container quick-services">
      {QUICK_SERVICES.map((item) => (
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
