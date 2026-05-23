import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import ProductPage from "./pages/ProductPage";
import CartPage from "./pages/CartPage";
import Toast from "./components/Toast";

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/product/:id" element={<ProductPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/login" element={<Navigate to="/auth" replace />} />
      </Routes>
      <Toast />
    </>
  );
}
