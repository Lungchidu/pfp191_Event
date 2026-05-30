/** Chỉ format hiển thị — không phải logic backend */
export function formatPrice(value) {
  return `${value.toLocaleString("vi-VN")}đ`;
}
