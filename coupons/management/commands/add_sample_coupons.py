"""
Thêm mã giảm giá mẫu (có thể là mã thật)
Usage: python manage.py add_sample_coupons
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from coupons.models import Coupon, Platform, Category

class Command(BaseCommand):
    help = 'Thêm mã giảm giá mẫu'

    def handle(self, *args, **options):
        # Lấy platforms
        try:
            shopee = Platform.objects.get(name='Shopee')
            lazada = Platform.objects.get(name='Lazada')
            tiktok = Platform.objects.get(name='TikTok Shop')
        except Platform.DoesNotExist:
            self.stdout.write(self.style.ERROR('Chưa có platforms! Chạy: python manage.py create_platforms'))
            return

        # Mã Shopee
        shopee_coupons = [
            {
                'code': 'SHOPEEXTRA',
                'title': 'Shopee Extra giảm 100K',
                'description': 'Giảm 100K cho đơn từ 500K',
                'discount_value': '100000đ',
                'min_order_value': 500000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'FREESHIP50K',
                'title': 'Freeship 50K Shopee',
                'description': 'Miễn phí vận chuyển 50K',
                'discount_value': '50000đ',
                'min_order_value': 0,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'SHOPEEPAY20',
                'title': 'ShopeePay giảm 20%',
                'description': 'Giảm 20% tối đa 50K khi thanh toán ShopeePay',
                'discount_value': '20%',
                'min_order_value': 100000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            }
        ]

        # Mã Lazada
        lazada_coupons = [
            {
                'code': 'LAZWALLET',
                'title': 'LazWallet giảm 15%',
                'description': 'Giảm 15% tối đa 100K khi dùng LazWallet',
                'discount_value': '15%',
                'min_order_value': 200000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'LAZNEW50',
                'title': 'Lazada mới giảm 50K',
                'description': 'Giảm 50K cho khách hàng mới',
                'discount_value': '50000đ',
                'min_order_value': 200000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'LAZFREE',
                'title': 'Freeship Lazada',
                'description': 'Miễn phí vận chuyển',
                'discount_value': '30000đ',
                'min_order_value': 0,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            }
        ]

        # Mã TikTok
        tiktok_coupons = [
            {
                'code': 'TIKTOK100K',
                'title': 'TikTok giảm 100K',
                'description': 'Giảm 100K cho đơn từ 300K',
                'discount_value': '100000đ',
                'min_order_value': 300000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'TTSHIP',
                'title': 'Freeship TikTok',
                'description': 'Miễn phí vận chuyển',
                'discount_value': '25000đ',
                'min_order_value': 0,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            },
            {
                'code': 'TTSALE15',
                'title': 'TikTok Sale 15%',
                'description': 'Giảm 15% tối đa 80K',
                'discount_value': '15%',
                'min_order_value': 200000,
                'expiry_date': datetime(2025, 12, 31, 23, 59, 59)
            }
        ]

        created_count = 0

        # Thêm Shopee coupons
        for data in shopee_coupons:
            coupon, created = Coupon.objects.get_or_create(
                code=data['code'],
                platform=shopee,
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'discount_value': data['discount_value'],
                    'min_order_value': data['min_order_value'],
                    'expiry_date': data['expiry_date'],
                    'status': 'approved'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ {coupon.code}'))

        # Thêm Lazada coupons
        for data in lazada_coupons:
            coupon, created = Coupon.objects.get_or_create(
                code=data['code'],
                platform=lazada,
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'discount_value': data['discount_value'],
                    'min_order_value': data['min_order_value'],
                    'expiry_date': data['expiry_date'],
                    'status': 'approved'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ {coupon.code}'))

        # Thêm TikTok coupons
        for data in tiktok_coupons:
            coupon, created = Coupon.objects.get_or_create(
                code=data['code'],
                platform=tiktok,
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'discount_value': data['discount_value'],
                    'min_order_value': data['min_order_value'],
                    'expiry_date': data['expiry_date'],
                    'status': 'approved'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ {coupon.code}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã thêm {created_count} mã giảm giá!'))
        self.stdout.write(f'Tổng coupons: {Coupon.objects.count()}')
