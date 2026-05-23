# Hướng dẫn publish EventRent

## Cách 1 — Netlify Drop (nhanh nhất, ~2 phút)

1. Chạy build (hoặc double-click `publish.bat`):
   ```powershell
   cd c:\Users\LEGION\event_rental
   npm run build
   copy build\index.html build\404.html
   ```
2. Mở [https://app.netlify.com/drop](https://app.netlify.com/drop) (đăng ký miễn phí nếu chưa có).
3. **Kéo thả** cả thư mục `build` vào trang.
4. Netlify trả link dạng `https://random-name.netlify.app` — web đã live.

Đổi tên site: Netlify Dashboard → Site settings → Change site name.

---

## Cách 2 — GitHub Pages (tự động mỗi lần push)

1. Tạo repo trên GitHub, push project lên nhánh `main`.
2. Trên GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Push code — workflow `.github/workflows/deploy.yml` sẽ build và publish.
4. Link: `https://<username>.github.io/<repo-name>/`

> Nếu repo không phải user site (`username.github.io`), thêm vào `package.json`:
> `"homepage": "https://<username>.github.io/<repo-name>"`
> rồi build lại.

---

## Cách 3 — Vercel

```powershell
npm i -g vercel
cd c:\Users\LEGION\event_rental
vercel --prod
```

Đăng nhập Vercel khi được hỏi. File `vercel.json` đã cấu hình SPA routing.

---

## Cách 4 — Netlify CLI

```powershell
npm i -g netlify-cli
npm run deploy:netlify
```

---

## Kiểm tra build trước khi publish

```powershell
npm run build
npm run preview
```

Mở `http://localhost:3000` (hoặc port `serve` hiển thị).

---

## Lưu ý

- Thư mục `build/` là bản production — **đây là thứ cần upload** (Netlify Drop).
- Routing React (`/auth`, `/product/1`, `/cart`) cần redirect SPA — đã có `public/_redirects` và `netlify.toml` / `vercel.json`.
- Dữ liệu hiện là mock; backend Python sẽ nối sau.
