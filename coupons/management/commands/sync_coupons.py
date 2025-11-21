"""
Django management command để đồng bộ coupons từ Supabase API
Usage: python manage.py sync_coupons --platform=shopee
       python manage.py sync_coupons --all
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import requests
from datetime import datetime
from coupons.models import Coupon, Platform

class Command(BaseCommand):
    help = 'Đồng bộ coupons từ Supabase API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            help='Tên platform: shopee, lazada, tiktok'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync tất cả platforms'
        )

    def handle(self, *args, **options):
        if options['all']:
            platforms = ['shopee', 'lazada', 'tiktok']
            for platform_name in platforms:
                self.sync_platform(platform_name)
        elif options['platform']:
            self.sync_platform(options['platform'])
        else:
            self.stdout.write(self.style.ERROR('Vui lòng chỉ định --platform hoặc --all'))

    def sync_platform(self, platform_name):
        """Đồng bộ coupons từ một platform"""
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'Đang sync {platform_name.upper()}...')
        self.stdout.write(f'{"="*60}')

        try:
            # Lấy platform từ database
            platform_map = {
                'shopee': 'Shopee',
                'lazada': 'Lazada',
                'tiktok': 'TikTok Shop'
            }
            
            platform = Platform.objects.get(name=platform_map[platform_name])
            
            # Gọi Supabase API
            url = f"{settings.SUPABASE_URL}/rest/v1/{platform_name}_coupons"
            headers = {
                "apikey": settings.SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}"
            }
            
            self.stdout.write(f'API URL: {url}')
            
            response = requests.get(
                url,
                headers=headers,
                params={"is_active": "eq.true"}
            )
            
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f'Lỗi API: {response.status_code} - {response.text}')
                )
                return
            
            coupons_data = response.json()
            self.stdout.write(f'Tìm thấy {len(coupons_data)} coupons từ API')
            
            # Đồng bộ vào database
            created_count = 0
            updated_count = 0
            
            for coupon_data in coupons_data:
                # Parse expiry_date
                expiry_date = datetime.fromisoformat(
                    coupon_data['expiry_date'].replace('Z', '+00:00')
                )
                
                # Update or create
                coupon, created = Coupon.objects.update_or_create(
                    api_source_id=coupon_data['id'],
                    platform=platform,
                    defaults={
                        'code': coupon_data['code'],
                        'title': coupon_data['title'],
                        'description': coupon_data.get('description', ''),
                        'discount_value': coupon_data['discount_value'],
                        'min_order_value': coupon_data.get('min_order_value', 0),
                        'quota': coupon_data.get('quota'),
                        'expiry_date': expiry_date,
                        'synced_from_api': True,
                        'status': 'approved'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Created: {coupon.code}')
                else:
                    updated_count += 1
                    self.stdout.write(f'  🔄 Updated: {coupon.code}')
            
            # Tổng kết
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Hoàn thành sync {platform_name.upper()}!'
            ))
            self.stdout.write(f'  - Tạo mới: {created_count}')
            self.stdout.write(f'  - Cập nhật: {updated_count}')
            self.stdout.write(f'  - Tổng: {created_count + updated_count}')
            
        except Platform.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Platform "{platform_name}" không tồn tại trong database')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Lỗi: {str(e)}')
            )
