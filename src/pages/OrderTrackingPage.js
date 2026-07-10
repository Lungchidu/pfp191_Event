import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchOrders } from "../services/shopApi";
import { useApp } from "../context/AppContext";
import { translations } from "../data/i18n";
import "../styles/orderTracking.css";

function mapApiOrderToFrontend(apiOrder, t) {
  let uiStatus = t.statusPending;
  let progress = 5;
  if (apiOrder.status === "pending") {
    uiStatus = t.statusPending;
    progress = 5;
  } else if (apiOrder.status === "confirmed") {
    uiStatus = t.statusConfirmed;
    progress = 30;
  } else if (apiOrder.status === "shipping") {
    uiStatus = t.statusShipping;
    progress = 65;
  } else if (apiOrder.status === "completed") {
    uiStatus = t.statusCompleted;
    progress = 100;
  } else if (apiOrder.status === "cancelled") {
    uiStatus = t.statusCancelled;
    progress = 0;
  }

  const steps = [
    { label: t.stepOrdered,   time: apiOrder.created_at || t.justNow, done: true },
    { label: t.stepConfirmed, time: progress >= 30 ? t.justNow : "—", done: progress >= 30 },
    { label: t.stepPickup,    time: progress >= 65 ? t.justNow : "—", done: progress >= 65 },
    { label: t.stepOnWay,     time: progress >= 65 ? t.justNow : "—", done: progress >= 65 },
    { label: t.stepDelivered, time: progress >= 100 ? t.justNow : "—", done: progress >= 100 },
  ];

  if (apiOrder.status === "cancelled") {
    steps.push({
      label: `${t.statusCancelled} (${apiOrder.note || "—"})`,
      time: t.justNow,
      done: true,
    });
  }

  const items = apiOrder.items || [];
  const itemNames = items.map((item) => item.product_name || item.name || "—").join(", ");
  const productText = itemNames || "—";

  const db_id = apiOrder.db_id || apiOrder.id || 0;
  const numericId =
    typeof db_id === "number"
      ? db_id
      : parseInt(String(db_id).replace(/\D/g, "")) || 0;

  const driverNames = ["Nguyễn Văn A", "Trần Văn B", "Lê Hoàng C", "Phạm Minh D"];
  const driver = progress >= 65 ? driverNames[numericId % driverNames.length] : "—";
  const phone = progress >= 65 ? `0901-234-56${numericId % 10}` : "—";

  let estDate = "—";
  if (apiOrder.created_at) {
    try {
      const dateParts = apiOrder.created_at.split(" ")[0].split("-");
      if (dateParts.length === 3) {
        const d = new Date(
          parseInt(dateParts[0]),
          parseInt(dateParts[1]) - 1,
          parseInt(dateParts[2]) + 2
        );
        estDate = `${String(d.getDate()).padStart(2, "0")}/${String(
          d.getMonth() + 1
        ).padStart(2, "0")}/${d.getFullYear()}`;
      }
    } catch {
      estDate = "17/06/2026";
    }
  }

  return {
    id: apiOrder.id,
    db_id: apiOrder.db_id,
    product: productText,
    status: uiStatus,
    progress: progress,
    estimatedDate: estDate,
    driver: driver,
    phone: phone,
    steps: steps,
    rawStatus: apiOrder.status,
  };
}

// ── Component chính ──────────────────────────────────────────────────────────

export default function OrderTrackingPage() {
  const navigate = useNavigate();
  const { lang } = useApp();
  const t = translations[lang] || translations.vi;

  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showCancelForm, setShowCancelForm] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelOther, setCancelOther] = useState("");
  const [cancelSuccess, setCancelSuccess] = useState(false);

  useEffect(() => {
    setLoadingOrders(true);
    fetchOrders()
      .then((apiOrders) => {
        if (apiOrders && apiOrders.length > 0) {
          const mapped = apiOrders
            .map((o) => mapApiOrderToFrontend(o, t))
            .filter(
              (o) =>
                o.rawStatus !== "completed" &&
                o.rawStatus !== "cancelled" &&
                o.rawStatus !== "returned"
            );
          setOrders(mapped);
        } else {
          setOrders([]);
        }
      })
      .catch(() => {
        const localRaw = JSON.parse(localStorage.getItem("local_orders") || "[]");
        const localMapped = localRaw
          .map((o) =>
            mapApiOrderToFrontend(
              { ...o, db_id: 0, items: o.items || [] },
              t
            )
          )
          .filter(
            (o) =>
              o.rawStatus !== "completed" &&
              o.rawStatus !== "cancelled" &&
              o.rawStatus !== "returned"
          );
        setOrders(localMapped);
      })
      .finally(() => setLoadingOrders(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]); // re-fetch / re-map when language changes

  const CANCEL_REASONS = t.cancelReasonList || [];

  // Real-time tracking simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setOrders((prevOrders) =>
        prevOrders.map((order) => {
          if (order.status === t.statusShipping) {
            const nextProgress = Math.min(order.progress + 1.2, 100);
            const isDone = nextProgress >= 100;
            const updatedSteps = order.steps.map((step, idx) => {
              if (idx === 4 && isDone) return { ...step, done: true, time: t.justNow };
              return step;
            });
            return {
              ...order,
              progress: parseFloat(nextProgress.toFixed(1)),
              status: isDone ? t.statusCompleted : order.status,
              steps: updatedSteps,
            };
          }
          if (order.status === t.statusPending) {
            const nextProgress = Math.min(order.progress + 0.4, 10);
            return {
              ...order,
              progress: parseFloat(nextProgress.toFixed(1)),
            };
          }
          return order;
        })
      );
    }, 3000);
    return () => clearInterval(interval);
  }, [t]);

  const activeOrder =
    orders.find((o) => o.id === selectedOrder?.id) || selectedOrder;
  const canCancel =
    activeOrder &&
    activeOrder.progress <= 10 &&
    activeOrder.status !== t.statusCancelled;

  const handleCancelSubmit = () => {
    if (!cancelReason) return;

    setOrders((prevOrders) =>
      prevOrders.map((order) =>
        order.id === activeOrder.id
          ? {
              ...order,
              status: t.statusCancelled,
              progress: 0,
              steps: [
                ...order.steps.map((s) => ({ ...s })),
                {
                  label: `${t.statusCancelled} (${
                    cancelReason === t.cancelOtherLabel ? cancelOther : cancelReason
                  })`,
                  time: t.justNow,
                  done: true,
                },
              ],
            }
          : order
      )
    );

    setCancelSuccess(true);
    setShowCancelForm(false);
    setTimeout(() => {
      setCancelSuccess(false);
      setSelectedOrder(null);
    }, 2500);
  };

  // ── Trang danh sách đơn hàng ─────────────────────────────────────────────
  if (!selectedOrder || !activeOrder) {
    return (
      <div className="ot-page">
        <div className="ot-topbar">
          <button className="ot-back-btn" onClick={() => navigate("/")}>
            ← {t.backToHome}
          </button>
          <h2 className="ot-title">
            <span className="ot-truck-icon">
              <svg viewBox="0 0 100 60" fill="currentColor" width="36" height="24">
                <rect x="30" y="8" width="55" height="32" rx="4" />
                <rect x="5" y="18" width="28" height="22" rx="3" />
                <polygon points="30,18 56,18 56,10 38,10" />
                <circle cx="20" cy="44" r="8" fill="currentColor" />
                <circle cx="20" cy="44" r="4" fill="white" />
                <circle cx="68" cy="44" r="8" fill="currentColor" />
                <circle cx="68" cy="44" r="4" fill="white" />
                <rect x="0" y="20" width="10" height="3" rx="1.5" opacity="0.6" />
                <rect x="0" y="26" width="14" height="3" rx="1.5" opacity="0.4" />
                <rect x="0" y="32" width="8" height="3" rx="1.5" opacity="0.5" />
              </svg>
            </span>
            {t.orderTracking}
          </h2>
        </div>

        {cancelSuccess && (
          <div className="ot-success-toast">{t.cancelledSuccess}</div>
        )}

        {loadingOrders ? (
          <div style={{ textAlign: "center", padding: "40px", color: "var(--color-muted)" }}>
            {t.loadingOrders}
          </div>
        ) : orders.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              padding: "48px 24px",
              background: "#fff",
              borderRadius: "12px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.05)",
              border: "1px solid #e2e8f0",
            }}
          >
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>📦</div>
            <h3 style={{ margin: "0 0 8px 0", fontSize: "18px", fontWeight: 700 }}>
              {t.noActiveOrders}
            </h3>
            <p style={{ margin: "0 0 20px 0", color: "#64748b", fontSize: "14px" }}>
              {t.noActiveOrdersDesc}
            </p>
            <button
              className="btn-primary"
              onClick={() => navigate("/")}
              style={{ padding: "10px 24px", borderRadius: "20px" }}
            >
              {t.rentNow}
            </button>
          </div>
        ) : (
          <div className="ot-list">
            {orders.map((order) => (
              <div
                key={order.id}
                className="ot-card"
                onClick={() => {
                  setSelectedOrder(order);
                  setShowCancelForm(false);
                  setCancelReason("");
                  setCancelOther("");
                }}
              >
                <div className="ot-card__header">
                  <span className="ot-card__id">{order.id}</span>
                  <span
                    className={`ot-badge ot-badge--${
                      order.rawStatus === "completed"
                        ? "done"
                        : order.rawStatus === "pending"
                        ? "pending"
                        : order.rawStatus === "cancelled"
                        ? "cancelled"
                        : "shipping"
                    }`}
                  >
                    {order.status}
                  </span>
                </div>
                <p className="ot-card__product">{order.product}</p>
                <div className="ot-progress-bar-wrap">
                  <div
                    className="ot-progress-bar-fill"
                    style={{ width: `${order.progress}%` }}
                  />
                </div>
                <p className="ot-card__eta">
                  {t.estDelivery} {order.estimatedDate}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Trang chi tiết đơn hàng ──────────────────────────────────────────────
  return (
    <div className="ot-page">
      <div className="ot-topbar">
        <button
          className="ot-back-btn"
          onClick={() => {
            setSelectedOrder(null);
            setShowCancelForm(false);
            setCancelReason("");
          }}
        >
          {t.backToList}
        </button>
        <h2 className="ot-title">
          {t.orderDetail}{activeOrder.id}
        </h2>
      </div>

      <div className="ot-detail">
        {/* Thông tin đơn */}
        <div className="ot-info-box">
          <div className="ot-info-row">
            <span>{t.productLabel}</span>
            <strong>{activeOrder.product}</strong>
          </div>
          <div className="ot-info-row">
            <span>{t.driverLabel}</span>
            <strong>{activeOrder.driver}</strong>
          </div>
          <div className="ot-info-row">
            <span>{t.contactLabel}</span>
            <strong>{activeOrder.phone}</strong>
          </div>
          <div className="ot-info-row">
            <span>{t.estDateLabel}</span>
            <strong>{activeOrder.estimatedDate}</strong>
          </div>
        </div>

        {/* Bản đồ định vị thời gian thực */}
        {activeOrder.rawStatus === "shipping" && (
          <div
            className="ot-section"
            style={{
              background: "#fff",
              borderRadius: "12px",
              padding: "20px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.06)",
              border: "1px solid #e2e8f0",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0", fontSize: "16px", fontWeight: 700, color: "#0f766e" }}>
              {t.realTimeTracking}
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px",
                background: "#f8fafc",
                padding: "12px",
                borderRadius: "8px",
                marginBottom: "16px",
                fontSize: "13px",
                color: "#334155",
              }}
            >
              <div>
                {t.distanceLabel}{" "}
                <strong style={{ color: "#0d9488", fontSize: "14px" }}>
                  {((100 - activeOrder.progress) * 0.1).toFixed(2)} km
                </strong>
              </div>
              <div>
                {t.etaLabel}{" "}
                <strong style={{ color: "#0d9488", fontSize: "14px" }}>
                  {Math.floor((100 - activeOrder.progress) * 0.4)}m{" "}
                  {Math.floor(((100 - activeOrder.progress) * 24) % 60)}s
                </strong>
              </div>
            </div>

            <div
              style={{
                background: "#f1f5f9",
                borderRadius: "10px",
                padding: "10px",
                position: "relative",
                overflow: "hidden",
              }}
            >
              <svg viewBox="0 0 400 120" style={{ width: "100%", height: "auto" }}>
                <path d="M 30 60 Q 200 20, 370 60" fill="none" stroke="#cbd5e1" strokeWidth="8" strokeLinecap="round" />
                <path
                  d="M 30 60 Q 200 20, 370 60"
                  fill="none"
                  stroke="#0d9488"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray="350"
                  strokeDashoffset={350 - (350 * activeOrder.progress) / 100}
                />
                <g transform="translate(15, 45)">
                  <circle cx="15" cy="15" r="10" fill="#475569" />
                  <text x="-5" y="-5" fill="#475569" fontSize="10" fontWeight="bold">
                    {t.warehouseLabel}
                  </text>
                </g>
                {(() => {
                  const p = activeOrder.progress / 100;
                  const x = 30 + 340 * p;
                  const y = (1 - p) * (1 - p) * 60 + 2 * (1 - p) * p * 20 + p * p * 60;
                  return (
                    <g transform={`translate(${x - 12}, ${y - 25})`}>
                      <circle
                        cx="12"
                        cy="12"
                        r="14"
                        fill="#0d9488"
                        style={{ filter: "drop-shadow(0 2px 4px rgba(13,148,136,0.3))" }}
                      />
                      <path
                        d="M6 15 h12 v-4 h-3 l-2 -3 h-7 z"
                        fill="#fff"
                        transform="scale(0.8) translate(3, 3)"
                      />
                      <circle cx="12" cy="12" r="18" fill="none" stroke="#0d9488" strokeWidth="1" opacity="0.6">
                        <animate attributeName="r" values="14;22;14" dur="2s" repeatCount="indefinite" />
                        <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite" />
                      </circle>
                    </g>
                  );
                })()}
                <g transform="translate(355, 45)">
                  <circle cx="15" cy="15" r="10" fill="#ef4444" />
                  <text x="-10" y="-5" fill="#ef4444" fontSize="10" fontWeight="bold">
                    {t.eventLabel}
                  </text>
                </g>
              </svg>
            </div>
          </div>
        )}

        {/* Thanh tiến trình */}
        <div className="ot-section">
          <p className="ot-section-label">
            {t.shippingProgress} <strong>{activeOrder.progress}%</strong>
          </p>
          <div className="ot-progress-bar-wrap ot-progress-bar-wrap--lg">
            <div
              className="ot-progress-bar-fill"
              style={{ width: `${activeOrder.progress}%` }}
            />
          </div>
        </div>

        {/* Timeline các bước */}
        <div className="ot-timeline">
          {activeOrder.steps.map((step, idx) => (
            <div key={idx} className={`ot-step ${step.done ? "ot-step--done" : ""}`}>
              <div className="ot-step__dot" />
              {idx < activeOrder.steps.length - 1 && <div className="ot-step__line" />}
              <div className="ot-step__content">
                <span className="ot-step__label">{step.label}</span>
                <span className="ot-step__time">{step.time}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Nút hủy đơn */}
        <div className="ot-cancel-section">
          {activeOrder.progress > 10 ? (
            <div className="ot-cancel-blocked">{t.cannotCancel}</div>
          ) : !showCancelForm ? (
            <button
              className="ot-cancel-btn"
              onClick={() => setShowCancelForm(true)}
            >
              {t.cancelOrder}
            </button>
          ) : null}

          {showCancelForm && canCancel && (
            <div className="ot-cancel-form">
              <h3 className="ot-cancel-form__title">{t.cancelReason}</h3>
              <div className="ot-reason-list">
                {CANCEL_REASONS.map((reason) => (
                  <label key={reason} className="ot-reason-item">
                    <input
                      type="radio"
                      name="cancelReason"
                      value={reason}
                      checked={cancelReason === reason}
                      onChange={() => setCancelReason(reason)}
                    />
                    <span>{reason}</span>
                  </label>
                ))}
              </div>

              {cancelReason === t.cancelOtherLabel && (
                <textarea
                  className="ot-cancel-textarea"
                  placeholder={t.cancelOtherPlaceholder}
                  value={cancelOther}
                  onChange={(e) => setCancelOther(e.target.value)}
                  rows={3}
                />
              )}

              <div className="ot-cancel-form__actions">
                <button
                  className="ot-btn ot-btn--secondary"
                  onClick={() => {
                    setShowCancelForm(false);
                    setCancelReason("");
                    setCancelOther("");
                  }}
                >
                  {t.cancelGoBack}
                </button>
                <button
                  className="ot-btn ot-btn--danger"
                  disabled={
                    !cancelReason ||
                    (cancelReason === t.cancelOtherLabel && !cancelOther.trim())
                  }
                  onClick={handleCancelSubmit}
                >
                  {t.cancelConfirm}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
