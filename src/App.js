import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProductPage from "./pages/ProductPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import OrderTrackingPage from "./pages/OrderTrackingPage";
import Toast from "./components/Toast";
import ProtectedRoute from "./components/ProtectedRoute";
import { saveUserFromUrl } from "./config/auth";
import RedirectToAuth from "./components/RedirectToAuth";
import AdminPage from "./pages/AdminPage";
import AccountPage from "./pages/AccountPage";

export default function App() {
  const [maintenanceMsg, setMaintenanceMsg] = useState("");

  useEffect(() => {
    saveUserFromUrl();
    
    const handleMaintenance = (e) => {
      setMaintenanceMsg(e.detail || "Hệ thống đang bảo trì, vui lòng thử lại sau ít phút");
    };
    
    window.addEventListener("maintenance_mode", handleMaintenance);
    return () => window.removeEventListener("maintenance_mode", handleMaintenance);
  }, []);

  if (maintenanceMsg) {
    return (
      <div style={{ display: 'flex', height: '100vh', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', color: '#333', textAlign: 'center', padding: '20px', fontFamily: 'sans-serif' }}>
        <div style={{ maxWidth: '600px', border: '1px solid #ddd', padding: '40px', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🛠️</div>
          <h1 style={{ fontSize: '1.8rem', marginBottom: '15px', color: '#e74c3c' }}>Hệ thống bảo trì</h1>
          <p style={{ fontSize: '1.1rem', lineHeight: '1.6', color: '#666' }}>{maintenanceMsg}</p>
        </div>
      </div>
    );
  }

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
        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/order-tracking"
          element={
            <ProtectedRoute>
              <OrderTrackingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <AccountPage />
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
