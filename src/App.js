import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProductPage from "./pages/ProductPage";
import CartPage from "./pages/CartPage";
import Toast from "./components/Toast";
import ProtectedRoute from "./components/ProtectedRoute";
import RedirectToAuth from "./components/RedirectToAuth";
import { saveUserFromUrl } from "./config/auth";

export default function App() {
  useEffect(() => {
    saveUserFromUrl();
  }, []);

  return (
    <>
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/product/:id"
          element={
            <ProtectedRoute>
              <ProductPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <CartPage />
            </ProtectedRoute>
          }
        />
        <Route path="/auth" element={<RedirectToAuth />} />
        <Route path="/login" element={<RedirectToAuth />} />
      </Routes>
      <Toast />
    </>
  );
}
