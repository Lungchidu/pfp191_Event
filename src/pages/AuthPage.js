import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { translations } from "../data/i18n";
import { AUTH_SERVER, TOKEN_KEY, USER_KEY } from "../config/auth";
import "../styles/auth.css";

const LANG_OPTIONS = [
  { code: "vi", label: "VN VI" },
  { code: "en", label: "GB EN" },
  { code: "jp", label: "JP JP" },
];

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const [lang, setLang] = useState("vi");
  const [isSignUp, setIsSignUp] = useState(
    searchParams.get("mode") !== "login"
  );
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: "",
    remember: false,
  });

  useEffect(() => {
    setIsSignUp(searchParams.get("mode") !== "login");
  }, [searchParams]);

  const t = translations[lang];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isSignUp) {
        const res = await fetch(`${AUTH_SERVER}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: form.email,
            password: form.password,
          }),
        });
        const result = await res.json();
        if (result.success) {
          alert("Đăng ký thành công! Vui lòng đăng nhập.");
          setIsSignUp(false);
        } else {
          alert(result.message);
        }
      } else {
        const res = await fetch(`${AUTH_SERVER}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: form.email,
            password: form.password,
          }),
        });
        const result = await res.json();
        if (result.success) {
          // Lưu token JWT (bảo mật hơn)
          localStorage.setItem(TOKEN_KEY, result.token);
          localStorage.setItem(USER_KEY, result.username || form.email);
          window.location.replace("/");
        } else {
          alert(result.message);
        }
      }
    } catch (err) {
      alert("Lỗi kết nối server. Vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-lang">
        {LANG_OPTIONS.map((opt) => (
          <button
            key={opt.code}
            type="button"
            className={lang === opt.code ? "active" : ""}
            onClick={() => setLang(opt.code)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className={`auth-card ${isSignUp ? "signup-mode" : "login-mode"}`}>
        <div className="auth-form-panel">
          <h1>{isSignUp ? t.signUp : t.signIn}</h1>

          <form onSubmit={handleSubmit}>
            {isSignUp && (
              <div className="auth-field">
                <input
                  type="text"
                  name="fullName"
                  placeholder={t.fullName}
                  value={form.fullName}
                  onChange={handleChange}
                  required
                />
              </div>
            )}

            <div className="auth-field">
              <input
                type="email"
                name="email"
                placeholder={t.email}
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="auth-field auth-password-wrap">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder={t.password}
                value={form.password}
                onChange={handleChange}
                required
                minLength={6}
              />
              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword((v) => !v)}
                aria-label="Toggle password"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {!isSignUp && (
              <div className="auth-remember">
                <label>
                  <input
                    type="checkbox"
                    name="remember"
                    checked={form.remember}
                    onChange={handleChange}
                  />
                  {t.rememberMe}
                </label>
                <a href="#forgot">{t.forgotPassword}</a>
              </div>
            )}

            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? "Đang xử lý..." : isSignUp ? t.signUpBtn : t.signInBtn}
            </button>
          </form>

          <div className="auth-divider">{t.orContinue}</div>

          <div className="auth-social">
            <button type="button" title="Google">G</button>
            <button type="button" title="Apple">⌘</button>
            <button type="button" title="Facebook">f</button>
          </div>

          <p className="auth-switch-text">
            {isSignUp ? t.haveAccount : t.noAccount}{" "}
            <button type="button" onClick={() => setIsSignUp((v) => !v)}>
              {isSignUp ? t.signIn : t.signUp}
            </button>
          </p>

          <Link to="/" className="auth-back-home">
            ← Về trang chủ
          </Link>
        </div>

        <div className="auth-welcome-panel">
          <h2>{isSignUp ? t.welcomeBack : t.joinUs}</h2>
          <p>{isSignUp ? t.welcomeDesc : t.joinDesc}</p>
          <button
            type="button"
            className="auth-panel-btn"
            onClick={() => setIsSignUp((v) => !v)}
          >
            {isSignUp ? t.signIn : t.signUp}
          </button>
        </div>
      </div>
    </div>
  );
}
