import { useEffect, useState } from "react";
import { HERO_SLIDES, SIDE_BANNERS } from "../../data/mockData";
import { useApp } from "../../context/AppContext";
import { translateHero, translateSideBanner } from "../../data/i18n";

export default function HeroSection() {
  const { updateFilters, lang } = useApp();
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActive((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

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
          {HERO_SLIDES.map((slide, index) => {
            const translatedSlide = translateHero(slide, lang);
            return (
              <div
                key={slide.id}
                className={`hero-carousel__slide ${
                  index === active ? "active" : ""
                }`}
              >
                <img src={translatedSlide.image} alt={translatedSlide.title} />
                <div className="hero-carousel__overlay">
                  <h2>
                    {translatedSlide.title.split("\n").map((line, i) => (
                      <span key={i}>
                        {i > 0 && <br />}
                        {line}
                      </span>
                    ))}
                  </h2>
                  <p>{translatedSlide.subtitle}</p>
                  <button
                    type="button"
                    className="hero-carousel__cta"
                    style={{ background: translatedSlide.accent }}
                    onClick={() => applyFilter(translatedSlide.filter)}
                  >
                    {translatedSlide.cta}
                  </button>
                </div>
              </div>
            );
          })}
          <div className="hero-carousel__dots">
            {HERO_SLIDES.map((slide, index) => (
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
          {SIDE_BANNERS.map((banner) => {
            const translatedBanner = translateSideBanner(banner, lang);
            return (
              <button
                key={banner.id}
                type="button"
                className="hero-side__card"
                onClick={() => applyFilter(translatedBanner.filter)}
              >
                <img src={translatedBanner.image} alt={translatedBanner.title} />
                <div className="hero-side__text">
                  <h4>{translatedBanner.title}</h4>
                  <p>{translatedBanner.desc}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

