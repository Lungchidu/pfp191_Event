import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { isLoggedIn } from "../config/auth";

export default function ProtectedRoute({ children }) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate("/auth?mode=login", { replace: true });
    }
  }, [navigate]);

  if (!isLoggedIn()) return null;
  return children;
}
