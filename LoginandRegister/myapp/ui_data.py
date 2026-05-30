# Dữ liệu giao diện trang chủ (trước đây nằm trong mockData.js)

QUICK_SERVICES = [
    {"id": "freeship", "label": "Giao miễn phí", "icon": "truck", "filter": {"query": "giao"}},
    {"id": "setup", "label": "Lắp đặt tại chỗ", "icon": "wrench", "filter": {"query": "lắp"}},
    {"id": "quote", "label": "Báo giá nhanh", "icon": "file", "filter": {"query": "combo"}},
    {"id": "track", "label": "Theo dõi vận chuyển", "icon": "map", "filter": {"categoryId": 14}},
    {"id": "hot", "label": "Thiết bị hot", "icon": "flame", "filter": {"minRating": 4.7}},
    {"id": "vip", "label": "Khách VIP", "icon": "crown", "filter": {"sortBy": "rating"}},
    {"id": "insurance", "label": "Bảo hiểm thiết bị", "icon": "shield", "filter": {"query": "bảo hiểm"}},
    {"id": "support", "label": "Hỗ trợ 24/7", "icon": "headphones", "filter": {"query": "hỗ trợ"}},
    {"id": "warehouse", "label": "Kho gần bạn", "icon": "warehouse", "filter": {"location": "Hồ Chí Minh"}},
    {"id": "event", "label": "Gói sự kiện", "icon": "calendar", "filter": {"categoryId": 16}},
]

HERO_SLIDES = [
    {
        "id": 1,
        "title": "Combo Âm thanh + Ánh sáng",
        "subtitle": "Giảm đến 35% cho đơn thuê từ 3 ngày",
        "cta": "Thuê ngay",
        "filter": {"categoryId": 16},
        "image": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=80",
        "accent": "#0d9488",
    },
    {
        "id": 2,
        "title": "Logistics sự kiện toàn quốc",
        "subtitle": "Giao – lắp – thu hồi trong 24h tại 3 miền",
        "cta": "Xem dịch vụ",
        "filter": {"categoryId": 14},
        "image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200&q=80",
        "accent": "#d97706",
    },
    {
        "id": 3,
        "title": "Nhà bạt & Sân khấu cao cấp",
        "subtitle": "Bảo hiểm thiết bị miễn phí cho đơn từ 5 triệu",
        "cta": "Khám phá",
        "filter": {"categoryId": 4},
        "image": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1200&q=80",
        "accent": "#7c3aed",
    },
]

SIDE_BANNERS = [
    {
        "id": 1,
        "title": "Flash thuê cuối tuần",
        "desc": "Chỉ còn 12 suất",
        "filter": {"flashOnly": True},
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&q=80",
    },
    {
        "id": 2,
        "title": "Setup miễn phí HCM",
        "desc": "Áp dụng đến 30/06",
        "filter": {"location": "Hồ Chí Minh"},
        "image": "https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2?w=600&q=80",
    },
]

TRENDING = [
    {"id": 1, "name": "Loa sự kiện", "count": "2.4k+", "icon": "volume", "keyword": "loa"},
    {"id": 2, "name": "Đèn sân khấu", "count": "1.8k+", "icon": "lightbulb", "keyword": "đèn"},
    {"id": 3, "name": "Nhà bạt", "count": "960+", "icon": "tent", "keyword": "nhà bạt"},
    {"id": 4, "name": "Màn LED", "count": "720+", "icon": "monitor", "keyword": "led"},
    {"id": 5, "name": "Logistics", "count": "540+", "icon": "package", "keyword": "logistics"},
    {"id": 6, "name": "Gói wedding", "count": "410+", "icon": "sparkles", "keyword": "wedding"},
]

POPULAR_SEARCHES = [
    "loa line array",
    "đèn beam",
    "nhà bạt",
    "sân khấu",
    "máy phát điện",
    "combo wedding",
]


def get_ui_data():
    return {
        "quickServices": QUICK_SERVICES,
        "heroSlides": HERO_SLIDES,
        "sideBanners": SIDE_BANNERS,
        "trending": TRENDING,
        "popularSearches": POPULAR_SEARCHES,
    }
