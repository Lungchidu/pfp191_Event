import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart } from "lucide-react";
import { POPULAR_SEARCHES } from "../../data/mockData";
import { useApp } from "../../context/AppContext";

export default function Header({ t, lang, onLangChange }) {
  const { filters, search, cartCount } = useApp();
  const [input, setInput] = useState(filters.query);
  const username = localStorage.getItem("username");

  useEffect(() => {
    setInput(filters.query);
  }, [filters.query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    search(input);
  };

  const handleLogout = () => {
    localStorage.removeItem("username");
    window.location.href = "/auth";
  };

  return (
    <>
      <div className="top-bar">
        <div className="container top-bar__inner">
          <div className="top-bar__links">
            <button type="button" className="top-bar__link-btn"
              onClick={() => alert("Kênh nhà cung cấp — sẽ kết nối backend sau.")}>
              {t.sellerCenter}
            </button>
            <button type="button" className="top-bar__link-btn"
              onClick={() => alert("Tải app EventRent — QR sẽ có khi publish.")}>
              {t.downloadApp}
            </button>
            <button type="button" className="top-bar__link-btn"