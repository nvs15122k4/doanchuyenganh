from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator


class CustomUserManager(UserManager):
    """Custom manager để tự động set role='admin' cho superuser"""
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')  # Tự động set role='admin'
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """Mở rộng User model với role"""
    email = models.EmailField(unique=True, null=False, blank=False)
    role = models.CharField(
        max_length=10,
        choices=[('user', 'User'), ('admin', 'Admin')],
        default='user',
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()  # Sử dụng custom manager

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Tự động set role='admin' nếu is_superuser=True
        if self.is_superuser and self.role != 'admin':
            self.role = 'admin'
        super().save(*args, **kwargs)


class Platform(models.Model):
    """Bảng Sàn TMĐT"""
    platform_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)
    logo_url = models.URLField(blank=True, null=True)
    api_endpoint = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platforms'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Bảng Danh mục"""
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Coupon(models.Model):
    """Bảng Mã giảm giá"""
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('expired', 'Hết hạn'),
    ]

    coupon_id = models.AutoField(primary_key=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=50, null=False)
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(blank=True)
    discount_value = models.CharField(max_length=50)  # "500k", "15%"
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quota = models.IntegerField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=False)
    affiliate_link = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        null=False
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_coupons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_from_api = models.BooleanField(default=False)
    api_source_id = models.CharField(max_length=100, blank=True, null=True)
    view_count = models.IntegerField(default=0)
    use_count = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, through='CouponCategory', related_name='coupons')
    
    # Affiliate Marketing Fields
    is_affiliate = models.BooleanField(default=False, help_text="Đánh dấu là mã tiếp thị liên kết")
    affiliate_commission = models.CharField(max_length=20, blank=True, null=True, help_text="Hoa hồng (VD: 5.5%, 50đ, 100K)")
    priority_score = models.IntegerField(default=0, help_text="Điểm ưu tiên hiển thị (càng cao càng ưu tiên)")
    is_featured = models.BooleanField(default=False, help_text="Hiển thị nổi bật")

    class Meta:
        db_table = 'coupons'
        ordering = ['-is_featured', '-priority_score', '-created_at']  # Ưu tiên affiliate trước

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expiry_date


class CouponCategory(models.Model):
    """Bảng trung gian N-N giữa Mã và Danh mục"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'coupon_categories'
        unique_together = [['coupon', 'category']]
        verbose_name_plural = 'Coupon Categories'


class UserSavedCoupon(models.Model):
    """Bảng lưu mã của người dùng N-N"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_saved_coupons'
        unique_together = [['user', 'coupon']]
        verbose_name_plural = 'User Saved Coupons'

    def __str__(self):
        return f"{self.user.email} saved {self.coupon.code}"


class SupportTicket(models.Model):
    """Bảng Ticket Hỗ trợ"""
    STATUS_CHOICES = [
        ('open', 'Đang mở'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết'),
        ('closed', 'Đã đóng'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
    ]
    
    ticket_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200, null=False)
    message = models.TextField(null=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        null=False
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        null=False
    )
    admin_response = models.TextField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ticket #{self.ticket_id} - {self.subject}"


class APIConfiguration(models.Model):
    """Cấu hình API cho các sàn TMĐT"""
    PLATFORM_CHOICES = [
        ('shopee', 'Shopee'),
        ('lazada', 'Lazada'),
        ('tiktok', 'TikTok Shop'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    api_url = models.URLField(help_text="API Endpoint URL")
    api_key = models.CharField(max_length=500, help_text="API Key/Token")
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_configurations'
        verbose_name = 'API Configuration'
        verbose_name_plural = 'API Configurations'
    
    def __str__(self):
        return f"{self.get_platform_display()} API"
