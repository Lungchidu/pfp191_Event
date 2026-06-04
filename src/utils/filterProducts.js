export function filterProducts(products, filters) {
  const {
    query = "",
    categoryId = null,
    location = "",
    minRating = 0,
    maxPrice = null,
    flashOnly = false,
    sortBy = "default",
  } = filters;

  const q = query.trim().toLowerCase();

  let result = products.filter((p) => {
    if (flashOnly && !p.isFlash) return false;
    if (categoryId && p.categoryId !== categoryId) return false;
    if (location && p.location !== location) return false;
    if (p.rating < minRating) return false;
    if (maxPrice != null && maxPrice > 0 && p.price > maxPrice) return false;

    if (!q) return true;

    const haystack = [
      p.name,
      p.description,
      p.location,
      ...(p.tags || []),
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(q);
  });

  if (sortBy === "price-asc") {
    result = [...result].sort((a, b) => a.price - b.price);
  } else if (sortBy === "price-desc") {
    result = [...result].sort((a, b) => b.price - a.price);
  } else if (sortBy === "rating") {
    result = [...result].sort((a, b) => b.rating - a.rating);
  }

  return result;
}
