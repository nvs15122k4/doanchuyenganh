from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from coupons.models import Platform, Category, Coupon, User


class Command(BaseCommand):
    help = 'Seed database with sample data for CouponHub'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Bắt đầu seed dữ liệu...'))

        # 1. Tạo Platforms
        self.stdout.write('📦 Tạo Platforms...')
        platforms_data = [
            {'name': 'Shopee', 'logo_url': 'https://cdn.shopee.vn/file/logo.png'},
            {'name': 'Lazada', 'logo_url': 'https://laz-img-cdn.alicdn.com/logo.png'},
            {'name': 'Tiki', 'logo_url': 'https://salt.tikicdn.com/logo.png'},
            {'name': 'TikTok Shop', 'logo_url': 'https://p16-tiktokcdn-com.akamaized.net/logo.png'},
        ]

        for p in platforms_data:
            platform, created = Platform.objects.get_or_create(
                name=p['name'], 
                defaults={'logo_url': p['logo_url']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo: {p["name"]}'))

        # 2. Tạo Categories
        self.stdout.write('📂 Tạo Categories...')
        categories_data = ['Thời trang', 'Điện tử', 'Thực phẩm', 'Làm đẹp', 'Đồ gia dụng', 'Sách', 'Thể thao']

        for cat in categories_data:
            category, created = Category.objects.get_or_create(name=cat)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo: {cat}'))

        # 3. Tạo Admin User (nếu chưa có)
        self.stdout.write('👤 Kiểm tra Admin User...')
        admin, created = User.objects.get_or_create(
            email='admin@couponhub.com',
            defaults={
                'username': 'admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Đã tạo Admin: admin@couponhub.com / admin123'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Admin đã tồn tại'))

        # 4. Tạo Coupons mẫu
        self.stdout.write('🎫 Tạo Coupons mẫu...')
        
        shopee = Platform.objects.get(name='Shopee')
        lazada = Platform.objects.get(name='Lazada')
        tiki = Platform.objects.get(name='Tiki')
        tiktok = Platform.objects.get(name='TikTok Shop')

        coupons_data = [
            # Shopee
            {
                'platform': shopee,
                'code': 'SHOPEE100K',
                'title': 'Giảm 100K cho đơn từ 500K',
                'description': 'Áp dụng cho tất cả sản phẩm. Số lượng có hạn!',
                'discount_value': '100,000đ',
                'min_order_value': 500000,
                'quota': 1000,
                'expiry_date': timezone.now() + timedelta(days=30),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': shopee,
                'code': 'FREESHIP50K',
                'title': 'Miễn phí vận chuyển 50K',
                'description': 'Freeship toàn quốc cho đơn từ 0đ',
                'discount_value': '50,000đ',
                'min_order_value': 0,
                'quota': 5000,
                'expiry_date': timezone.now() + timedelta(days=15),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': shopee,
                'code': 'FLASHSALE20',
                'title': 'Giảm 20% Flash Sale',
                'description': 'Giảm tối đa 200K cho Flash Sale 12h',
                'discount_value': '20%',
                'min_order_value': 100000,
                'quota': 500,
                'expiry_date': timezone.now() + timedelta(days=7),
                'status': 'approved',
                'created_by': admin,
            },
            
            # Lazada
            {
                'platform': lazada,
                'code': 'LAZADA200K',
                'title': 'Voucher 200K cho đơn 1 triệu',
                'description': 'Mã giảm giá độc quyền Lazada',
                'discount_value': '200,000đ',
                'min_order_value': 1000000,
                'quota': 800,
                'expiry_date': timezone.now() + timedelta(days=20),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': lazada,
                'code': 'LAZFREE',
                'title': 'Miễn phí vận chuyển',
                'description': 'Freeship không giới hạn',
                'discount_value': 'Freeship',
                'min_order_value': 0,
                'quota': 10000,
                'expiry_date': timezone.now() + timedelta(days=30),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': lazada,
                'code': 'SALE30',
                'title': 'Giảm 30% Điện tử',
                'description': 'Giảm tối đa 300K cho danh mục Điện tử',
                'discount_value': '30%',
                'min_order_value': 500000,
                'quota': 300,
                'expiry_date': timezone.now() + timedelta(days=10),
                'status': 'approved',
                'created_by': admin,
            },
            
            # Tiki
            {
                'platform': tiki,
                'code': 'TIKI150K',
                'title': 'Giảm 150K đơn từ 800K',
                'description': 'Áp dụng cho tất cả sản phẩm tại Tiki',
                'discount_value': '150,000đ',
                'min_order_value': 800000,
                'quota': 600,
                'expiry_date': timezone.now() + timedelta(days=25),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': tiki,
                'code': 'TIKISACH',
                'title': 'Giảm 25% sách',
                'description': 'Giảm tối đa 50K cho danh mục Sách',
                'discount_value': '25%',
                'min_order_value': 100000,
                'quota': 2000,
                'expiry_date': timezone.now() + timedelta(days=15),
                'status': 'approved',
                'created_by': admin,
            },
            
            # TikTok Shop
            {
                'platform': tiktok,
                'code': 'TIKTOK100',
                'title': 'Giảm 100K TikTok Shop',
                'description': 'Mã độc quyền cho người dùng mới',
                'discount_value': '100,000đ',
                'min_order_value': 300000,
                'quota': 1500,
                'expiry_date': timezone.now() + timedelta(days=30),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': tiktok,
                'code': 'TIKTOKFREE',
                'title': 'Freeship TikTok',
                'description': 'Miễn phí vận chuyển toàn quốc',
                'discount_value': 'Freeship',
                'min_order_value': 0,
                'quota': 5000,
                'expiry_date': timezone.now() + timedelta(days=20),
                'status': 'approved',
                'created_by': admin,
            },
            {
                'platform': tiktok,
                'code': 'SALE15',
                'title': 'Giảm 15% thời trang',
                'description': 'Giảm tối đa 100K cho Thời trang',
                'discount_value': '15%',
                'min_order_value': 200000,
                'quota': 800,
                'expiry_date': timezone.now() + timedelta(days=12),
                'status': 'approved',
                'created_by': admin,
            },
        ]

        coupon_count = 0
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                coupon_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo: {coupon_data["code"]}'))

        # 5. Thống kê
        self.stdout.write(self.style.SUCCESS('\n📊 THỐNG KÊ:'))
        self.stdout.write(f'  - Platforms: {Platform.objects.count()}')
        self.stdout.write(f'  - Categories: {Category.objects.count()}')
        self.stdout.write(f'  - Coupons: {Coupon.objects.count()}')
        self.stdout.write(f'  - Users: {User.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\n🎉 HOÀN TẤT! Seed dữ liệu thành công.'))
        self.stdout.write(self.style.WARNING('\n💡 Thông tin đăng nhập Admin:'))
        self.stdout.write('   Email: admin@couponhub.com')
        self.stdout.write('   Password: admin123')