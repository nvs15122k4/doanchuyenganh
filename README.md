CouponHub - Hệ thống Quản lý Mã giảm giá

Hệ thống quản lý và chia sẻ mã giảm giá từ các sàn thương mại điện tử hàng đầu Việt Nam.

## Tính năng

### Trang chủ
- Tìm kiếm mã giảm giá
- Lọc nhanh theo sàn (Shopee, Lazada, TikTok)
- Hiển thị mã giảm giá HOT
- Banner quảng cáo

### Trang chi tiết mã
- Hiển thị đầy đủ thông tin mã giảm giá
- Copy mã nhanh chóng
- Lưu mã vào danh sách cá nhân (yêu cầu đăng nhập)
- Nút "Dùng ngay" chuyển hướng đến sàn TMĐT

### Trang người dùng
- Xem danh sách mã đã lưu
- Quản lý mã đã lưu (bỏ lưu)
- Copy và sử dụng mã nhanh

### Trang quản trị
- Dashboard với thống kê cơ bản
- CRUD mã giảm giá (Thêm, Sửa, Xóa)
- Quản lý sàn TMĐT
- Quản lý người dùng
- Lọc và tìm kiếm mã giảm giá

## Công nghệ sử dụng

- **Backend:** Django 5.2.8 (Python)
- **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
- **Database:** MySQL (có thể dùng SQLite cho development)
- **API:** REST API endpoints

## 📦 Cài đặt

### 1. Clone repository hoặc giải nén project

### 2. Tạo và kích hoạt virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình Database

#### MySQL (Production)
- Các giá trị mặc định đã được cấu hình sẵn trong `settings.py`:
  - `DB_NAME = couponhub`
  - `DB_USER = admin`
  - `DB_PASSWORD = 1234`
  - `DB_HOST = localhost`
  - `DB_PORT = 3306`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'couponhub'),
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', '1234'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}
```
Sau khi tạo database, chạy:
```bash
mysql -u admin -p1234 < sql/schema.sql
```
hoặc chạy migrations như bình thường (`python manage.py migrate`).

### 5. Chạy migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser (Admin)

```bash
python manage.py createsuperuser
```

Nhập email, username và password. Để tạo admin, sau khi đăng nhập vào Django admin, chỉnh sửa user và đặt `role = 'admin'`.

### 7. Tạo dữ liệu mẫu (Tùy chọn)

Chạy script Python để tạo dữ liệu mẫu:

```bash
python manage.py shell
```

Sau đó chạy:

```python
from coupons.models import Platform, Category, Coupon, User
from django.utils import timezone
from datetime import timedelta

# Tạo sàn
shopee = Platform.objects.create(name='Shopee', logo_url='')
lazada = Platform.objects.create(name='Lazada', logo_url='')
tiktok = Platform.objects.create(name='TikTok', logo_url='')

# Tạo mã giảm giá mẫu
admin_user = User.objects.filter(role='admin').first()
if admin_user:
    Coupon.objects.create(
        platform=shopee,
        code='FREESHIP',
        title='Miễn phí vận chuyển',
        description='Giảm 100% phí vận chuyển',
        discount_value='500k',
        min_order_value=0,
        quota=100,
        expiry_date=timezone.now() + timedelta(days=30),
        affiliate_link='https://shopee.vn',
        status='approved',
        created_by=admin_user
    )
```

### 8. Chạy server

```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## Tài khoản mặc định

Sau khi tạo superuser, đăng nhập vào Django admin và chỉnh sửa user để đặt `role = 'admin'` để có quyền truy cập trang quản trị.

## API Endpoints

### Lấy danh sách mã giảm giá
```
GET /api/coupons/?search=keyword&platform=1&status=approved
```

### Lấy chi tiết mã
```
GET /api/coupons/{coupon_id}/
```

### Lấy danh sách sàn
```
GET /api/platforms/
```

### Lấy dữ liệu từ Supabase
```
GET /api/supabase/coupons/?limit=12
```

### Đồng bộ voucher từ các sàn
```
GET /admin/integrations/vouchers/  (yêu cầu tài khoản admin)
```

## Tích hợp Supabase

- Cấu hình tại `settings.py` hoặc biến môi trường:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_COUPONS_TABLE` (mặc định: `coupons`)
- Trang chủ hiển thị thêm section "Mã giảm giá từ Supabase".
- API riêng `/api/supabase/coupons/` giúp kiểm tra nhanh dữ liệu nhận được.

## Marketplace APIs (Lazada, Shopee, TikTok Shop)

Để gọi trực tiếp các API chính thức, cần cấu hình thêm các biến môi trường:

```
LAZADA_APP_KEY=...
LAZADA_APP_SECRET=...
LAZADA_ACCESS_TOKEN=...

SHOPEE_PARTNER_ID=...
SHOPEE_PARTNER_KEY=...
SHOPEE_SHOP_ID=...
SHOPEE_ACCESS_TOKEN=...

TIKTOK_APP_KEY=...
TIKTOK_APP_SECRET=...
TIKTOK_SHOP_CIPHER=...
TIKTOK_ACCESS_TOKEN=...
```

Sau khi thiết lập, truy cập `/admin/integrations/vouchers/` để lấy JSON tổng hợp từ 3 sàn TMĐT.

## UI/UX

- Sử dụng Tailwind CSS cho styling
- Responsive design (mobile-friendly)
- Icon từ Font Awesome
- Alpine.js cho các tương tác JavaScript đơn giản

## Ghi chú

- Dự án này sử dụng SUPABASE concept nhưng được triển khai trực tiếp với Django REST API
- Database có thể chuyển đổi giữa SQLite (dev) và MySQL (production)
- Tất cả các chức năng đã được triển khai đầy đủ theo yêu cầu

## 🚀 Deploy lên Render + Railway MySQL

Xem hướng dẫn chi tiết trong folder **`../docs/`**

### Các bước nhanh (15 phút):

1. **Tạo MySQL trên Railway:** https://railway.app
2. **Kiểm tra code:** `python ../docs/check_deploy.py`
3. **Tạo SECRET_KEY:** `python ../docs/generate_secret_key.py`
4. **Push lên GitHub**
5. **Deploy Web lên Render:** https://render.com
6. **Tạo superuser và test**

✅ Website sẽ online tại: `https://couponhub.onrender.com`

💰 Chi phí: **$0** (Hoàn toàn miễn phí)

📖 **Hướng dẫn chi tiết:** Xem file `../docs/DEPLOY.md`

## Tác giả

Nguyễn Văn Sang - Đồ án tốt nghiệp - CouponHub
