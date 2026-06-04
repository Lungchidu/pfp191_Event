import { LOCATIONS } from "../../data/mockData";
import { useApp } from "../../context/AppContext";

export default function ProductFilters({ t }) {
  const { filters, updateFilters, clearFilters, filteredProducts } =
    useApp();

  return (
    <section className="container filters-bar" id="catalog">
      <div className="filters-bar__row">
        <h2 className="filters-bar__title">
          {t.catalogTitle}{" "}
          <span className="filters-bar__count">
            ({filteredProducts.length} {t.results})
          </span>
        </h2>
        {(filters.query ||
          filters.categoryId ||
          filters.location ||
          filters.minRating > 0 ||
          filters.maxPrice ||
          filters.flashOnly) && (
          <button
            type="button"
            className="filters-bar__clear"
            onClick={clearFilters}
          >
            {t.clearFilters}
          </button>
        )}
      </div>

      <div className="filters-bar__controls">
        <select
          value={filters.location}
          onChange={(e) =>
            updateFilters({ location: e.target.value })
          }
          aria-label={t.filterLocation}
        >
          <option value="">{t.allLocations}</option>
          {LOCATIONS.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>

        <select
          value={filters.minRating}
          onChange={(e) =>
            updateFilters({ minRating: Number(e.target.value) })
          }
          aria-label={t.filterRating}
        >
          <option value={0}>{t.allRatings}</option>
          <option value={4}>4+ ⭐</option>
          <option value={4.5}>4.5+ ⭐</option>
          <option value={4.8}>4.8+ ⭐</option>
        </select>

        <input
          type="number"
          placeholder={t.maxPrice}
          value={filters.maxPrice || ""}
          onChange={(e) =>
            updateFilters({
              maxPrice: e.target.value
                ? Number(e.target.value)
                : null,
            })
          }
          min={0}
          step={100000}
        />

        <input
          type="date"
          value={filters.rentalDate || ""}
          onChange={(e) =>
            updateFilters({ rentalDate: e.target.value })
          }
          aria-label={t.rentalDate}
        />

        <select
          value={filters.sortBy}
          onChange={(e) =>
            updateFilters({ sortBy: e.target.value })
          }
          aria-label={t.sortBy}
        >
          <option value="default">{t.sortDefault}</option>
          <option value="price-asc">{t.sortPriceAsc}</option>
          <option value="price-desc">{t.sortPriceDesc}</option>
          <option value="rating">{t.sortRating}</option>
        </select>

        <label className="filters-bar__checkbox">
          <input
            type="checkbox"
            checked={filters.flashOnly}
            onChange={(e) =>
              updateFilters({ flashOnly: e.target.checked })
            }
          />
          {t.flashOnly}
        </label>
      </div>

      {filters.query && (
        <p className="filters-bar__active">
          {t.searchingFor}: <strong>"{filters.query}"</strong>
        </p>
      )}
    </section>
  );
}
