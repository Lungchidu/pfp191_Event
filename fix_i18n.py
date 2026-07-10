import os

file_path = "c:\\Users\\LEGION\\Desktop\\pfp191_Event\\src\\data\\i18n.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the start of sideBannerTranslations
index = content.find("export const sideBannerTranslations = {")
if index != -1:
    content = content[:index]

rest = """export const sideBannerTranslations = {
  en: {
    1: {
      title: "Weekend Flash Rental",
      desc: "Only 12 slots left"
    },
    2: {
      title: "Free Setup in HCMC",
      desc: "Valid until June 30th"
    }
  }
};

export const trendingTranslations = {
  en: {
    1: "Event Speakers",
    2: "Stage Lighting",
    3: "Event Tents",
    4: "LED Wall",
    5: "Logistics",
    6: "Wedding Combo"
  }
};

export function translateProduct(product, lang) {
  if (lang !== "en" || !product) return product;
  const trans = productTranslations.en[product.id] || {};
  return {
    ...product,
    name: product.name_en || trans.name || product.name,
    description: product.description_en || trans.description || product.description,
    specs: trans.specs || product.specs,
    location: locationTranslations.en[product.location] || product.location
  };
}

export function translateCategory(cat, lang) {
  if (lang !== "en" || !cat) return cat;
  const name = categoryTranslations.en[cat.id];
  if (!name) return cat;
  return { ...cat, name };
}

export function translateService(srv, lang) {
  if (lang !== "en" || !srv) return srv;
  const label = serviceTranslations.en[srv.id];
  if (!label) return srv;
  return { ...srv, label };
}

export function translateLocation(loc, lang) {
  if (lang !== "en") return loc;
  return locationTranslations.en[loc] || loc;
}

export function translateHero(slide, lang) {
  if (lang !== "en" || !slide) return slide;
  const trans = heroTranslations.en[slide.id];
  if (!trans) return slide;
  return {
    ...slide,
    title: trans.title || slide.title,
    subtitle: trans.subtitle || slide.subtitle,
    cta: trans.cta || slide.cta
  };
}

export function translateSideBanner(banner, lang) {
  if (lang !== "en" || !banner) return banner;
  const trans = sideBannerTranslations.en[banner.id];
  if (!trans) return banner;
  return {
    ...banner,
    title: trans.title || banner.title,
    desc: trans.desc || banner.desc
  };
}

export function translateTrending(trend, lang) {
  if (lang !== "en" || !trend) return trend;
  const name = trendingTranslations.en[trend.id];
  if (!name) return trend;
  return { ...trend, name };
}
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content + rest)
