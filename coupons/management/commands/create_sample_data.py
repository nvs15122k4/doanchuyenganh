from django.core.management.base import BaseCommand
from coupons.models import Platform, Category, Coupon, User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho CouponHub'

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu mẫu...')

        # Tạo sàn
        shopee, created = Platform.objects.get_or_create(
            name='Shopee',
            defaults={'logo_url': 'https://cf.shopee.vn/file/a5a589c8e1182e877209aef32709a5f5'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Đã tạo sàn: {shopee.name}'))

        lazada, created = Platform.objects.get_or_create(
            name='Lazada',
            defaults={'logo_url': ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Đã tạo sàn: {lazada.name}'))

        tiktok, created = Platform.objects.get_or_create(
            name='TikTok',
            defaults={'logo_url': ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Đã tạo sàn: {tiktok.name}'))

        # Tạo danh mục
        categories_data = ['Thời trang', 'Điện tử', 'Ăn uống', 'Làm đẹp', 'Sức khỏe']
        for cat_name in categories_data:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Đã tạo danh mục: {category.name}'))

        # Tạo admin user nếu chưa có
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@couponhub.com',
                password='admin123',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Đã tạo admin user: admin@couponhub.com / admin123'))

        # Tạo mã giảm giá mẫu
        sample_coupons = [
            {
                'platform': shopee,
                'code': 'FREESHIP',
                'title': 'Miễn phí vận chuyển',
                'description': 'Giảm 100% phí vận chuyển cho đơn hàng',
                'discount_value': '500k',
                'min_order_value': 0,
                'quota': 100,
                'affiliate_link': 'https://shopee.vn',
            },
            {
                'platform': shopee,
                'code': 'SALE15',
                'title': 'Giảm 15%',
                'description': 'Giảm 15% cho đơn hàng từ 500k',
                'discount_value': '15%',
                'min_order_value': 500000,
                'quota': 50,
                'affiliate_link': 'https://shopee.vn',
            },
            {
                'platform': lazada,
                'code': 'LAZADA20',
                'title': 'Giảm 20%',
                'description': 'Giảm 20% cho tất cả sản phẩm',
                'discount_value': '20%',
                'min_order_value': 0,
                'quota': 200,
                'affiliate_link': 'https://www.lazada.vn',
            },
            {
                'platform': tiktok,
                'code': 'TIKTOK10',
                'title': 'Giảm 10%',
                'description': 'Giảm 10% cho đơn hàng đầu tiên',
                'discount_value': '10%',
                'min_order_value': 100000,
                'quota': 300,
                'affiliate_link': 'https://www.tiktokshop.vn',
            },
        ]

        for coupon_data in sample_coupons:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults={
                    **coupon_data,
                    'expiry_date': timezone.now() + timedelta(days=30),
                    'status': 'approved',
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Đã tạo mã: {coupon.code}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Hoàn thành tạo dữ liệu mẫu!'))
        self.stdout.write(self.style.WARNING('\nTài khoản admin: admin@couponhub.com / admin123'))



