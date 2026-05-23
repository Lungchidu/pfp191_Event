export const QUICK_SERVICES = [
  { id: "freeship", label: "Giao miễn phí", icon: "truck", filter: { query: "giao" } },
  { id: "setup", label: "Lắp đặt tại chỗ", icon: "wrench", filter: { query: "lắp" } },
  { id: "quote", label: "Báo giá nhanh", icon: "file", filter: { query: "combo" } },
  { id: "track", label: "Theo dõi vận chuyển", icon: "map", filter: { categoryId: 14 } },
  { id: "hot", label: "Thiết bị hot", icon: "flame", filter: { minRating: 4.7 } },
  { id: "vip", label: "Khách VIP", icon: "crown", filter: { sortBy: "rating" } },
  { id: "insurance", label: "Bảo hiểm thiết bị", icon: "shield", filter: { query: "bảo hiểm" } },
  { id: "support", label: "Hỗ trợ 24/7", icon: "headphones", filter: { query: "hỗ trợ" } },
  { id: "warehouse", label: "Kho gần bạn", icon: "warehouse", filter: { location: "Hồ Chí Minh" } },
  { id: "event", label: "Gói sự kiện", icon: "calendar", filter: { categoryId: 16 } },
];

export const CATEGORIES = [
  { id: 1, name: "Âm thanh", icon: "volume" },
  { id: 2, name: "Ánh sáng", icon: "lightbulb" },
  { id: 3, name: "Sân khấu", icon: "stage" },
  { id: 4, name: "Nhà bạt", icon: "tent" },
  { id: 5, name: "Bàn ghế", icon: "chair" },
  { id: 6, name: "Màn hình LED", icon: "monitor" },
  { id: 7, name: "Máy chiếu", icon: "projector" },
  { id: 8, name: "Micro & DJ", icon: "mic" },
  { id: 9, name: "Generator", icon: "zap" },
  { id: 10, name: "Dây & Phụ kiện", icon: "cable" },
  { id: 11, name: "Trang trí", icon: "sparkles" },
  { id: 12, name: "Backline", icon: "guitar" },
  { id: 13, name: "Camera live", icon: "camera" },
  { id: 14, name: "Logistics", icon: "package" },
  { id: 15, name: "Nhân sự kỹ thuật", icon: "users" },
  { id: 16, name: "Gói combo", icon: "boxes" },
];

export const LOCATIONS = [
  "Hồ Chí Minh",
  "Hà Nội",
  "Đà Nẵng",
];

export const PRODUCTS = [
  {
    id: 1,
    name: "Loa line array 12 inch",
    description:
      "Hệ thống loa line array công suất cao, phù hợp sân khấu ngoài trời 500–2000 khách. Bao gồm amply và dây tín hiệu.",
    price: 850000,
    originalPrice: 1200000,
    discount: 29,
    sold: 72,
    stock: 100,
    rating: 4.8,
    location: "Hồ Chí Minh",
    categoryId: 1,
    isFlash: true,
    tags: ["loa", "âm thanh", "line array"],
    image:
      "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&q=80",
    specs: ["Công suất 2000W", "Bluetooth/Dante", "Kèm stand"],
  },
  {
    id: 2,
    name: "Đèn moving head beam 380",
    description:
      "Đèn beam 380W, 16 màu, phù hợp club và sự kiện. Hỗ trợ DMX512, có chế độ auto.",
    price: 420000,
    originalPrice: 580000,
    discount: 28,
    sold: 45,
    stock: 60,
    rating: 4.7,
    location: "Hà Nội",
    categoryId: 2,
    isFlash: true,
    tags: ["đèn", "beam", "ánh sáng"],
    image:
      "https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?w=800&q=80",
    specs: ["380W", "DMX512", "Góc beam 3°"],
  },
  {
    id: 3,
    name: "Sân khấu 6x4m gấp",
    description:
      "Khung sân khấu nhôm gấp, mặt sàn gỗ chống trượt. Lắp đặt trong 2 giờ, có kỹ thuật viên đi kèm.",
    price: 2100000,
    originalPrice: 2800000,
    discount: 25,
    sold: 18,
    stock: 30,
    rating: 4.9,
    location: "Đà Nẵng",
    categoryId: 3,
    isFlash: true,
    tags: ["sân khấu", "lắp đặt"],
    image:
      "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800&q=80",
    specs: ["6x4m", "Tải 500kg/m²", "Kèm lắp đặt"],
  },
  {
    id: 4,
    name: "Nhà bạt 10x20m",
    description:
      "Nhà bạt khung nhôm, mái PVC chống UV. Phù hợp hội chợ, wedding outdoor.",
    price: 3500000,
    originalPrice: 4500000,
    discount: 22,
    sold: 9,
    stock: 20,
    rating: 4.6,
    location: "Hồ Chí Minh",
    categoryId: 4,
    isFlash: true,
    tags: ["nhà bạt", "wedding", "ngoài trời"],
    image:
      "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=800&q=80",
    specs: ["10x20m", "Chống UV", "Kèm neo"],
  },
  {
    id: 5,
    name: "Máy phát điện 20KVA",
    description:
      "Máy phát diesel 20KVA, im lặng, đủ công suất cho sân khấu vừa.",
    price: 1800000,
    originalPrice: 2400000,
    discount: 25,
    sold: 31,
    stock: 50,
    rating: 4.5,
    location: "Hà Nội",
    categoryId: 9,
    isFlash: true,
    tags: ["máy phát điện", "generator"],
    image:
      "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800&q=80",
    specs: ["20KVA", "Diesel", "Ồn < 75dB"],
  },
  {
    id: 6,
    name: "LED wall P3.9 indoor",
    description:
      "Màn hình LED trong nhà độ phân giải cao, module P3.9, kèm processor.",
    price: 5200000,
    originalPrice: 6800000,
    discount: 24,
    sold: 6,
    stock: 15,
    rating: 4.9,
    location: "Hồ Chí Minh",
    categoryId: 6,
    isFlash: true,
    tags: ["led", "màn hình"],
    image:
      "https://images.unsplash.com/photo-1598488035139-bdcb86d0b0b2?w=800&q=80",
    specs: ["P3.9", "Indoor", "Kèm processor"],
  },
  {
    id: 7,
    name: "Loa JBL EON 715",
    description: "Loa active 15 inch, bluetooth, phù hợp hội thảo và tiệc nhỏ.",
    price: 500000,
    originalPrice: 650000,
    discount: 23,
    sold: 88,
    stock: 120,
    rating: 4.6,
    location: "Hồ Chí Minh",
    categoryId: 1,
    isFlash: false,
    tags: ["loa", "JBL"],
    image:
      "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80",
    specs: ["15 inch", "1300W", "Bluetooth"],
  },
  {
    id: 8,
    name: "Bàn tròn sự kiện + ghế",
    description: "Combo 10 bàn tròn kèm 80 ghế banquet, vải trắng.",
    price: 150000,
    originalPrice: 200000,
    discount: 25,
    sold: 120,
    stock: 200,
    rating: 4.4,
    location: "Đà Nẵng",
    categoryId: 5,
    isFlash: false,
    tags: ["bàn ghế", "wedding"],
    image:
      "https://images.unsplash.com/photo-1464366400600-6394ab3a9c32?w=800&q=80",
    specs: ["10 bàn", "80 ghế", "Kèm phủ"],
  },
  {
    id: 9,
    name: "Gói logistics sự kiện 24h",
    description:
      "Vận chuyển – lắp đặt – thu hồi thiết bị trong 24h nội thành HCM.",
    price: 800000,
    originalPrice: 1000000,
    discount: 20,
    sold: 55,
    stock: 80,
    rating: 4.7,
    location: "Hồ Chí Minh",
    categoryId: 14,
    isFlash: false,
    tags: ["logistics", "giao hàng", "lắp đặt"],
    image:
      "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80",
    specs: ["24h", "Nội thành HCM", "Kèm bảo hiểm"],
  },
  {
    id: 10,
    name: "Combo wedding âm thanh + ánh sáng",
    description:
      "Trọn gói loa, đèn par, sương khói cho tiệc cưới 200 khách.",
    price: 4500000,
    originalPrice: 6000000,
    discount: 25,
    sold: 34,
    stock: 40,
    rating: 4.9,
    location: "Hà Nội",
    categoryId: 16,
    isFlash: false,
    tags: ["combo", "wedding", "combo wedding"],
    image:
      "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&q=80",
    specs: ["200 khách", "Kỹ thuật 2 người", "Rehearsal 1 buổi"],
  },
  {
    id: 11,
    name: "Máy chiếu 8000 lumens",
    description: "Máy chiếu Full HD, độ sáng 8000lm, kèm màn 120 inch.",
    price: 600000,
    originalPrice: 800000,
    discount: 25,
    sold: 42,
    stock: 60,
    rating: 4.5,
    location: "Hà Nội",
    categoryId: 7,
    isFlash: false,
    tags: ["máy chiếu", "projector"],
    image:
      "https://images.unsplash.com/photo-1478720568477-152d9b164e63?w=800&q=80",
    specs: ["8000lm", "Full HD", "Màn 120 inch"],
  },
  {
    id: 12,
    name: "Bộ micro không dây Shure",
    description: "2 micro cầm + 1 micro cài áo, receiver UHF.",
    price: 350000,
    originalPrice: 450000,
    discount: 22,
    sold: 67,
    stock: 90,
    rating: 4.8,
    location: "Hồ Chí Minh",
    categoryId: 8,
    isFlash: false,
    tags: ["micro", "shure"],
    image:
      "https://images.unsplash.com/photo-1598488035139-bdcb86d0b0b2?w=800&q=80",
    specs: ["UHF", "3 micro", "Pin 8h"],
  },
];

export const FLASH_PRODUCTS = PRODUCTS.filter((p) => p.isFlash);

export const HERO_SLIDES = [
  {
    id: 1,
    title: "Combo Âm thanh + Ánh sáng",
    subtitle: "Giảm đến 35% cho đơn thuê từ 3 ngày",
    cta: "Thuê ngay",
    filter: { categoryId: 16 },
    image:
      "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=80",
    accent: "#0d9488",
  },
  {
    id: 2,
    title: "Logistics sự kiện toàn quốc",
    subtitle: "Giao – lắp – thu hồi trong 24h tại 3 miền",
    cta: "Xem dịch vụ",
    filter: { categoryId: 14 },
    image:
      "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200&q=80",
    accent: "#d97706",
  },
  {
    id: 3,
    title: "Nhà bạt & Sân khấu cao cấp",
    subtitle: "Bảo hiểm thiết bị miễn phí cho đơn từ 5 triệu",
    cta: "Khám phá",
    filter: { categoryId: 4 },
    image:
      "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1200&q=80",
    accent: "#7c3aed",
  },
];

export const SIDE_BANNERS = [
  {
    id: 1,
    title: "Flash thuê cuối tuần",
    desc: "Chỉ còn 12 suất",
    filter: { flashOnly: true },
    image:
      "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&q=80",
  },
  {
    id: 2,
    title: "Setup miễn phí HCM",
    desc: "Áp dụng đến 30/06",
    filter: { location: "Hồ Chí Minh" },
    image:
      "https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?w=600&q=80",
  },
];

export const TRENDING = [
  { id: 1, name: "Loa sự kiện", count: "2.4k+", icon: "volume", keyword: "loa" },
  { id: 2, name: "Đèn sân khấu", count: "1.8k+", icon: "lightbulb", keyword: "đèn" },
  { id: 3, name: "Nhà bạt", count: "960+", icon: "tent", keyword: "nhà bạt" },
  { id: 4, name: "Màn LED", count: "720+", icon: "monitor", keyword: "led" },
  { id: 5, name: "Logistics", count: "540+", icon: "package", keyword: "logistics" },
  { id: 6, name: "Gói wedding", count: "410+", icon: "sparkles", keyword: "wedding" },
];

export const POPULAR_SEARCHES = [
  "loa line array",
  "đèn beam",
  "nhà bạt",
  "sân khấu",
  "máy phát điện",
  "combo wedding",
];

export const formatPrice = (value) =>
  `${value.toLocaleString("vi-VN")}đ`;
