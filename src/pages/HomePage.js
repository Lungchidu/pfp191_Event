import { translations } from "../data/i18n";
import Header from "../components/home/Header";
import HeroSection from "../components/home/HeroSection";
import PromoBanner from "../components/home/PromoBanner";
import CategoryGrid from "../components/home/CategoryGrid";
import FlashRental from "../components/home/FlashRental";
import TrendingCategories from "../components/home/TrendingCategories";
import ProductFilters from "../components/home/ProductFilters";
import ProductGrid from "../components/home/ProductGrid";
import Footer from "../components/home/Footer";
import { useApp } from "../context/AppContext";
import "../styles/home.css";

export default function HomePage() {
  const { lang, setLang } = useApp();
  const t = translations[lang] || translations.vi;

  return (
    <div className="home-page">
      <Header t={t} lang={lang} onLangChange={setLang} />
      <HeroSection />
      <PromoBanner t={t} />
      <CategoryGrid title={t.categories} />
      <FlashRental title={t.flashSale} seeMore={t.seeMore} />
      <TrendingCategories title={t.trending} />
      <ProductFilters t={t} />
      <ProductGrid t={t} />
      <Footer />
    </div>
  );
}

