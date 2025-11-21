# ✅ CouponHub Setup Checklist

## 📋 Pre-Setup

- [ ] Python 3.8+ đã cài đặt
- [ ] MySQL đã cài đặt và đang chạy
- [ ] Có tài khoản Supabase (https://supabase.com)
- [ ] Git đã cài đặt (optional)

## 🗄️ Database Setup

### Supabase
- [ ] Đã tạo project: https://lxoyximmjfsoswxkctlv.supabase.co
- [ ] Đã chạy `sql/schema_supabase.sql` trên SQL Editor
- [ ] Kiểm tra 3 bảng đã tạo: shopee_coupons, lazada_coupons, tiktok_coupons
- [ ] Mỗi bảng có 5 records (tổng 15 coupons)
- [ ] Test API: `python sql/test_supabase_connection.py` → 3/3 pass

### MySQL
- [ ] Đã import `sql/schema_mysql.sql`
- [ ] Database `couponhub` đã tạo
- [ ] 8 bảng đã tạo: platforms, users, categories, coupons, etc.
- [ ] Sample data: 3 platforms, 7 categories
- [ ] Test connection: `mysql -u root -p couponhub -e "SHOW TABLES;"` → 8 tables

## 🐍 Python Environment

- [ ] Virtual environment đã tạo: `python -m venv venv`
- [ ] Virtual environment đã activate
- [ ] Dependencies đã cài: `pip install -r requirements.txt`
- [ ] Không có lỗi khi import: `python -c "import django, requests, pymysql"`

## ⚙️ Django Configuration

- [ ] File `.env` đã tạo (copy từ `.env.example`)
- [ ] Supabase credentials đã điền đúng
- [ ] MySQL credentials đã điền đúng
- [ ] `python manage.py check` → No issues
- [ ] `python manage.py makemigrations` → No changes
- [ ] `python manage.py migrate` → OK

## 🔄 Data Sync

- [ ] Sync Shopee: `python manage.py sync_coupons --platform=shopee` → 5 coupons
- [ ] Sync Lazada: `python manage.py sync_coupons --platform=lazada` → 5 coupons
- [ ] Sync TikTok: `python manage.py sync_coupons --platform=tiktok` → 5 coupons
- [ ] Tổng coupons trong MySQL: 15 coupons
- [ ] Kiểm tra: `SELECT COUNT(*) FROM coupons WHERE synced_from_api = TRUE;` → 15

## 🧪 Testing

- [ ] Test system: `python test_full_system.py` → 4/4 tests pass
  - [ ] Supabase API connection
  - [ ] MySQL connection
  - [ ] Django models
  - [ ] Django settings

## 🚀 Run Application

- [ ] Server chạy: `python manage.py runserver`
- [ ] Truy cập được: http://localhost:8000
- [ ] Không có lỗi trong console
- [ ] Trang home hiển thị coupons

## 👤 Admin Setup (Optional)

- [ ] Tạo superuser: `python manage.py createsuperuser`
- [ ] Đăng nhập admin: http://localhost:8000/admin
- [ ] Xem được platforms, coupons, categories

## 📊 Verification

### Supabase Dashboard
- [ ] Tables > shopee_coupons → 5 rows
- [ ] Tables > lazada_coupons → 5 rows
- [ ] Tables > tiktok_coupons → 5 rows
- [ ] API Logs → Không có lỗi

### MySQL Database
```sql
USE couponhub;
SELECT COUNT(*) FROM platforms;   -- 3
SELECT COUNT(*) FROM categories;  -- 7
SELECT COUNT(*) FROM coupons;     -- 15 (sau sync)
SELECT * FROM v_platform_stats;   -- Thống kê
```

### Django Shell
```python
from coupons.models import *
Platform.objects.count()  # 3
Category.objects.count()  # 7
Coupon.objects.count()    # 15
Coupon.objects.filter(synced_from_api=True).count()  # 15
```

## 🎉 Final Check

- [ ] Tất cả tests pass
- [ ] Không có error trong logs
- [ ] API endpoints hoạt động
- [ ] Sync command hoạt động
- [ ] Web interface hiển thị đúng

## 📝 Notes

- Nếu có lỗi, xem: `sql/TROUBLESHOOTING.md`
- Hướng dẫn chi tiết: `SETUP_SUPABASE.md`
- Setup nhanh: `QUICK_SETUP.md`

---

**Status**: [ ] Setup hoàn tất ✅
