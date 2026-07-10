import { useApp } from "../../context/AppContext";
import { translations } from "../../data/i18n";

export default function Footer() {
  const { lang } = useApp();
  const t = translations[lang] || translations.vi;

  return (
    <footer className="site-footer">
      <div className="container site-footer__grid">
        <div>
          <h4>{t.aboutEventRent}</h4>
          <ul>
            <li>{t.aboutUs}</li>
            <li>{t.careers}</li>
            <li>{t.terms}</li>
          </ul>
        </div>
        <div>
          <h4>{t.supportLabel}</h4>
          <ul>
            <li>{t.helpCenter}</li>
            <li>{t.rentalGuide}</li>
            <li>{t.insurancePolicy}</li>
          </ul>
        </div>
        <div>
          <h4>{t.logisticsLabel}</h4>
          <ul>
            <li>{t.shippingTracking}</li>
            <li>{t.logisticsQuote}</li>
            <li>{t.onsiteInstall}</li>
          </ul>
        </div>
        <div>
          <h4>{t.contactLabel}</h4>
          <ul>
            <li>hotline@eventrent.vn</li>
            <li>1900 xxxx</li>
            <li>{t.locations}</li>
          </ul>
        </div>
      </div>
      <div className="container site-footer__bottom">
        © 2026 EventRent — Event Equipment Rental & Logistics
      </div>
    </footer>
  );
}

