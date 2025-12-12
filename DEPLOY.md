# 🚀 HƯỚNG DẪN DEPLOY LÊN RENDER.COM VỚI MYSQL

## ⏱️ Thời gian: 15 phút

---

## BƯỚC 1: Chuẩn bị Code (3 phút)

### 1.1. Kiểm tra cấu hình
```bash
cd CouponHub
python check_deploy.py
```
Phải thấy: ✅ TẤT CẢ KIỂM TRA PASS

### 1.2. Tạo SECRET_KEY mới
```bash
python generate_secret_key.py
```
**📋 Copy và lưu lại key này!**

### 1.3. Push code lên GitHub

**Nếu chưa có repo:**
```bash
git init
git add .
git commit -m "Ready for deployment"
git branch -M main
git remote add origin https://github.com/<username>/CouponHub.git
git push -u origin main
```

**Nếu đã có repo:**
```bash
git add .
git commit -m "Update for deployment"
git push
```

---

## BƯỚC 2: Tạo MySQL Database trên Render (4 phút)

### 2.1. Đăng nhập Render
- Vào: https://render.com
- Click **"Get Started"** hoặc **"Sign In"**
- Chọn **"Sign in with GitHub"**

### 2.2. Tạo MySQL Database
1. Click **"New +"** (góc trên bên phải)
2. Chọn **"MySQL"**
3. Điền thông tin:
   - **Name**: `couponhub-mysql`
   - **Database**: `couponhub`
   - **User**: `admin`
   - **Region**: Singapore (gần Việt Nam nhất)
   - **MySQL Version**: 8.0
   - **Plan**: Free

4. Click **"Create Database"**

### 2.3. Lấy thông tin kết nối
Sau khi tạo xong, vào tab **"Info"**, copy các thông tin:
- **Internal Database URL** (dạng: `mysql://admin:...@...`)
- **Hostname**
- **Port**
- **Database**
- **Username**
- **Password**

**📋 Lưu lại tất cả thông tin này!**

---

## BƯỚC 3: Tạo Web Service (5 phút)

### 3.1. Tạo Web Service
1. Click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"** → **"Next"**
3. Chọn repository **CouponHub** của bạn
4. Click **"Connect"**

### 3.2. Cấu hình Service
Điền thông tin:

- **Name**: `couponhub` (hoặc tên bạn muốn)
- **Region**: Singapore
- **Branch**: `main`
- **Root Directory**: để trống
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command**: 
  ```
  gunicorn CouponHub.wsgi:application
  ```
- **Plan**: Free

### 3.3. Thêm Environment Variables
Scroll xuống phần **"Environment Variables"**, click **"Add Environment Variable"**

Thêm các biến sau (thay `<...>` bằng giá trị thật):

```
DJANGO_SECRET_KEY=<paste-key-từ-bước-1.2>
DJANGO_ALLOWED_HOSTS=.render.com
DEBUG=False

DB_ENGINE=django.db.backends.mysql
DB_NAME=couponhub
DB_USER=admin
DB_PASSWORD=<password-từ-mysql-bước-2.3>
DB_HOST=<hostname-từ-mysql-bước-2.3>
DB_PORT=<port-từ-mysql-bước-2.3>
```

**Ví dụ:**
```
DJANGO_SECRET_KEY=django-insecure-abc123xyz...
DJANGO_ALLOWED_HOSTS=.render.com
DEBUG=False

DB_ENGINE=django.db.backends.mysql
DB_NAME=couponhub
DB_USER=admin
DB_PASSWORD=aBc123XyZ456...
DB_HOST=dpg-abc123-singapore-do-user-123456.render.com
DB_PORT=3306
```

### 3.4. Deploy
- Click **"Create Web Service"**
- Render sẽ bắt đầu build và deploy
- Xem logs để theo dõi tiến trình
- Đợi 5-10 phút

**Dấu hiệu thành công:**
- Logs hiện: `Starting gunicorn`
- Status chuyển sang: **"Live"** (màu xanh)

---

## BƯỚC 4: Tạo Admin Account (2 phút)

### 4.1. Mở Shell
- Vào dashboard của web service
- Click tab **"Shell"** (bên cạnh Logs)
- Đợi terminal load

### 4.2. Tạo superuser
Trong shell, chạy:
```bash
python manage.py createsuperuser
```

Nhập thông tin:
```
Email: admin@couponhub.com
Username: admin
Password: ******** (mật khẩu của bạn)
Password (again): ********
```

Thấy "Superuser created successfully" là OK!

---

## BƯỚC 5: Kiểm tra Website (1 phút)

### 5.1. Truy cập website
URL của bạn sẽ là:
```
https://couponhub.onrender.com
```
(hoặc tên bạn đặt ở bước 3.2)

### 5.2. Đăng nhập admin
```
https://couponhub.onrender.com/admin
```
- Username: `admin`
- Password: (mật khẩu vừa tạo)

### 5.3. Tạo dữ liệu mẫu

**Tạo Platforms:**
1. Vào **Platforms** → **Add Platform**
2. Tạo 3 platforms:
   - Name: `Shopee`, Logo URL: (để trống hoặc thêm link)
   - Name: `Lazada`, Logo URL: (để trống hoặc thêm link)
   - Name: `TikTok Shop`, Logo URL: (để trống hoặc thêm link)

**Tạo Coupons:**
1. Vào **Coupons** → **Add Coupon**
2. Tạo vài mã giảm giá mẫu:
   - Platform: Shopee
   - Code: `FREESHIP50K`
   - Title: `Miễn phí vận chuyển đơn 50k`
   - Description: `Áp dụng cho đơn hàng từ 50.000đ`
   - Discount Value: `50k`
   - Status: `Approved`
   - Expiry Date: (chọn ngày tương lai)

### 5.4. Test các chức năng
- ✅ Trang chủ hiển thị mã giảm giá
- ✅ Tìm kiếm hoạt động
- ✅ Lọc theo platform
- ✅ Đăng ký tài khoản user
- ✅ Đăng nhập user
- ✅ Lưu mã giảm giá
- ✅ Copy mã

---

## ✅ HOÀN THÀNH!

Website của bạn đã online tại:
```
🌐 https://couponhub.onrender.com
```

---

## 🔧 Xử lý lỗi thường gặp

### ❌ Build failed: "No module named 'MySQLdb'"
**Nguyên nhân:** Thiếu PyMySQL

**Giải pháp:**
- Kiểm tra `requirements.txt` có `PyMySQL==1.1.0`
- Redeploy: Click **"Manual Deploy"** → **"Deploy latest commit"**

### ❌ "Can't connect to MySQL server"
**Nguyên nhân:** Sai thông tin database

**Giải pháp:**
1. Vào MySQL database → tab **"Info"**
2. Copy lại: Hostname, Port, Password
3. Vào Web Service → **"Environment"**
4. Cập nhật lại `DB_HOST`, `DB_PORT`, `DB_PASSWORD`
5. Service sẽ tự động restart

### ❌ DisallowedHost at /
**Nguyên nhân:** ALLOWED_HOSTS chưa đúng

**Giải pháp:**
- Vào **"Environment"**
- Kiểm tra `DJANGO_ALLOWED_HOSTS=.render.com`
- Hoặc thêm domain cụ thể: `couponhub.onrender.com,.render.com`

### ❌ Static files không load (CSS/JS)
**Nguyên nhân:** Chưa chạy collectstatic

**Giải pháp:**
- Vào **"Shell"**
- Chạy: `python manage.py collectstatic --noinput`
- Hoặc redeploy

### ❌ 500 Internal Server Error
**Giải pháp:**
1. Xem **Logs** để biết lỗi cụ thể
2. Vào **Shell**, chạy:
   ```bash
   python manage.py migrate
   python manage.py check
   ```
3. Nếu cần debug, tạm thời đặt `DEBUG=True` trong Environment

### ❌ Website "ngủ" sau 15 phút
**Nguyên nhân:** Free tier của Render

**Giải pháp:**
- Hoàn toàn bình thường với free plan
- Lần đầu truy cập sẽ mất 30-60 giây để "thức dậy"
- Nếu muốn website luôn online: nâng cấp lên paid plan ($7/tháng)

---

## 🔄 Cập nhật Code

Mỗi khi sửa code:

```bash
git add .
git commit -m "Update features"
git push
```

Render sẽ **tự động deploy** lại! Không cần làm gì thêm.

---

## 📱 Sử dụng Domain riêng (Tùy chọn)

### Nếu bạn có domain (vd: couponhub.com):

1. **Trên Render:**
   - Vào Web Service → **"Settings"**
   - Scroll xuống **"Custom Domain"**
   - Click **"Add Custom Domain"**
   - Nhập: `couponhub.com` và `www.couponhub.com`

2. **Trên nhà cung cấp domain (GoDaddy, Namecheap, etc.):**
   - Thêm DNS records theo hướng dẫn của Render
   - Thường là CNAME record trỏ về Render

3. **Cập nhật Environment:**
   ```
   DJANGO_ALLOWED_HOSTS=couponhub.com,www.couponhub.com,.render.com
   ```

4. **Đợi DNS propagate** (5-30 phút)

---

## 💡 Tips & Best Practices

### 1. Bảo mật
- ✅ Luôn đặt `DEBUG=False` trên production
- ✅ SECRET_KEY phải khác với development
- ✅ Không commit file `.env` vào Git
- ✅ Đổi password admin định kỳ

### 2. Performance
- ✅ Render Free tier đủ cho demo/portfolio
- ✅ Nếu traffic cao: nâng cấp database và web service
- ✅ Cân nhắc dùng CDN cho static files

### 3. Backup
- ✅ Render tự động backup MySQL database
- ✅ Có thể export database từ tab "Backups"
- ✅ Nên backup code trên GitHub thường xuyên

### 4. Monitoring
- ✅ Xem Logs thường xuyên để phát hiện lỗi
- ✅ Render gửi email nếu service down
- ✅ Có thể tích hợp Sentry để track errors

---

## 📞 Cần trợ giúp?

- **Render Docs:** https://render.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **Community:** https://community.render.com

---

## 📊 So sánh Plans

| Feature | Free | Starter ($7/mo) |
|---------|------|-----------------|
| Website | ✅ | ✅ |
| SSL/HTTPS | ✅ | ✅ |
| Auto-deploy | ✅ | ✅ |
| Sleep after 15min | ❌ | ✅ Always on |
| Build time | Slower | Faster |
| Database | 1GB | 10GB+ |

Free plan hoàn toàn đủ cho demo và portfolio!

---

**🎉 Chúc mừng bạn đã deploy thành công CouponHub!**

Chia sẻ link website với bạn bè và nhà tuyển dụng nhé! 🚀
