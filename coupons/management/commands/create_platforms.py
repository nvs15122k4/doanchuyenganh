"""
Django management command để tạo platforms
Usage: python manage.py create_platforms
"""

from django.core.management.base import BaseCommand
from coupons.models import Platform

class Command(BaseCommand):
    help = 'Tạo platforms (Shopee, Lazada, TikTok Shop)'

    def handle(self, *args, **options):
        platforms_data = [
            {
                'name': 'Shopee',
                'logo_url': 'https://cdn.shopee.vn/logo.png',
                'api_endpoint': 'https://lxoyximmjfsoswxkctlv.supabase.co/rest/v1/shopee_coupons'
            },
            {
                'name': 'Lazada',
                'logo_url': 'https://cdn.lazada.vn/logo.png',
                'api_endpoint': 'https://lxoyximmjfsoswxkctlv.supabase.co/rest/v1/lazada_coupons'
            },
            {
                'name': 'TikTok Shop',
                'logo_url': 'https://cdn.tiktokshop.vn/logo.png',
                'api_endpoint': 'https://lxoyximmjfsoswxkctlv.supabase.co/rest/v1/tiktok_coupons'
            }
        ]

        for data in platforms_data:
            platform, created = Platform.objects.get_or_create(
                name=data['name'],
                defaults={
                    'logo_url': data['logo_url'],
                    'api_endpoint': data['api_endpoint']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created: {platform.name}'))
            else:
                self.stdout.write(f'⏭️  Already exists: {platform.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Total platforms: {Platform.objects.count()}'))
