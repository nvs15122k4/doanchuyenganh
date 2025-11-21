from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Platform, Category, Coupon, CouponCategory, UserSavedCoupon


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('role',)}),
    )


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo_url']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class CouponCategoryInline(admin.TabularInline):
    model = CouponCategory
    extra = 1


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'platform', 'discount_value', 'is_affiliate', 'is_featured', 'priority_score', 'status', 'expiry_date']
    list_filter = ['status', 'platform', 'is_affiliate', 'is_featured', 'created_at']
    search_fields = ['code', 'title', 'description']
    readonly_fields = ['created_at', 'view_count', 'use_count']
    inlines = [CouponCategoryInline]
    list_editable = ['is_affiliate', 'is_featured', 'priority_score']  # Chỉnh nhanh
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'title', 'description', 'platform')
        }),
        ('Chi tiết giảm giá', {
            'fields': ('discount_value', 'min_order_value', 'quota', 'expiry_date')
        }),
        ('Liên kết và trạng thái', {
            'fields': ('affiliate_link', 'status', 'created_by')
        }),
        ('🎯 Tiếp thị liên kết (Affiliate)', {
            'fields': ('is_affiliate', 'affiliate_commission', 'priority_score', 'is_featured'),
            'classes': ('collapse',),
            'description': 'Cấu hình cho mã giảm giá affiliate - ưu tiên hiển thị và hoa hồng'
        }),
        ('Thống kê', {
            'fields': ('view_count', 'use_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponCategory)
class CouponCategoryAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'category']


@admin.register(UserSavedCoupon)
class UserSavedCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__email', 'coupon__code']
