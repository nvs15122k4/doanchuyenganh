# ⚡ QUICKSTART - DEPLOY TRONG 15 PHÚT

## 📋 Chuẩn bị

```bash
# 1. Kiểm tra
python check_deploy.py

# 2. Tạo SECRET_KEY
python generate_secret_key.py
# → Copy key này!

# 3. Push lên GitHub
git add .
git commit -m "Ready to deploy"
git push
```

---

## 🚀 Deploy trên Render.com

### Bước 1: Tạo MySQL Database
1. Vào https://render.com → Đăng nhập GitHub
2. **New +** → **MySQL**
3. Name: `couponhub-mysql`, Database: `couponhub`, User: `admin`
4. **Create Database**
5. **📋 Copy:** Hostname, Port, Password

### Bước 2: Tạo Web Service
1. **New +** → **Web Service**
2. Chọn repo **CouponHub**
3. Cấu hình:
   - Name: `couponhub`
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start: `gunicorn CouponHub.wsgi:application`

### Bước 3: Environment Variables
```
DJANGO_SECRET_KEY=<key-từ-bước-chuẩn-bị>
DJANGO_ALLOWED_HOSTS=.render.com
DEBUG=False

DB_ENGINE=django.db.backends.mysql
DB_NAME=couponhub
DB_USER=admin
DB_PASSWORD=<password-từ-mysql>
DB_HOST=<hostname-từ-mysql>
DB_PORT=<port-từ-mysql>
```

### Bước 4: Deploy
- Click **Create Web Service**
- Đợi 5-10 phút

### Bước 5: Tạo Admin
- Vào tab **Shell**
- Chạy: `python manage.py createsuperuser`

---

## ✅ Xong!

Website: `https://couponhub.onrender.com`

Admin: `https://couponhub.onrender.com/admin`

---

📖 **Chi tiết:** Xem file [DEPLOY.md](DEPLOY.md)
