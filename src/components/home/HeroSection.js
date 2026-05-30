import { useEffect, useState } from "react";
import { useApp } from "../../context/AppContext";

export default function HeroSection() {
  const { ui, updateFilters } = useApp();
  const [active, setActive] = useState(0);

  const heroSlides = ui?.heroSlides || [];
  const sideBanners = ui?.sideBanners || [];

  useEffect(() => {
    if (heroSlides.length === 0) return undefined;
    const timer = setInterval(() => {
      setActive((prev) => (prev + 1) % heroSlides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [heroSlides.length]);

  if (heroSlides.length === 0) return null;

  const applyFilter = (filter) => {
    updateFilters(
      { ...filter, query: filter.query || "" },
      { scrollToCatalog: true }
    );
  };

  return (
    <section className="hero-section container">
      <div className="hero-grid">
        <div className="hero-carousel">
          {heroSlides.map((slide, index) => (
            <div
              key={slide.id}
              className={`hero-carousel__slide ${
                index === active ? "active" : ""
              }`}
            >
              <img src={slide.image} alt={slide.title} />
              <div className="hero-carousel__overlay">
                <h2>{slide.title}</h2>
                <p>{slide.subtitle}</p>
                <button
                  type="button"
                  className="hero-carousel__cta"
                  style={{ background: slide.accent }}
                  onClick={() => applyFilter(slide.filter)}
                >
                  {slide.cta}
                </button>
              </div>
            </div>
          ))}
          <div className="hero-carousel__dots">
            {heroSlides.map((slide, index) => (
              <button
                key={slide.id}
                type="button"
                className={index === active ? "active" : ""}
                onClick={() => setActive(index)}
                aria-label={`Slide ${index + 1}`}
              />
            ))}
          </div>
        </div>

        <div className="hero-side">
          {sideBanners.map((banner) => (
            <button
              key={banner.id}
              type="button"
              className="hero-side__card"
              onClick={() => applyFilter(banner.filter)}
            >
              <img src={banner.image} alt={banner.title} />
              <div className="hero-side__text">
                <h4>{banner.title}</h4>
                <p>{banner.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
