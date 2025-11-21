import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from coupons.models import Platform, Category, Coupon, User


class Command(BaseCommand):
    help = 'Import real coupon data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--shopee',
            type=str,
            help='Path to Shopee CSV file'
        )
        parser.add_argument(
            '--lazada',
            type=str,
            help='Path to Lazada CSV file'
        )
        parser.add_argument(
            '--tiktok',
            type=str,
            help='Path to TikTok CSV file'
        )

    def handle(self, *args, **options):
        # Get or create admin user
        admin, _ = User.objects.get_or_create(
            email='admin@couponhub.com',
            defaults={
                'username': 'admin',
                'role': 'admin',
                'is_staff': True
            }
        )

        # Import Shopee
        if options['shopee']:
            self.import_shopee(options['shopee'], admin)

        # Import Lazada
        if options['lazada']:
            self.import_lazada(options['lazada'], admin)

        # Import TikTok
        if options['tiktok']:
            self.import_tiktok(options['tiktok'], admin)

    def import_shopee(self, file_path, admin):
        """
        Import Shopee coupons from CSV
        Expected columns: code, title, description, discount_value, min_order_value, quota, expiry_date
        """
        platform = Platform.objects.get(name='Shopee')
        count = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse expiry date (format: YYYY-MM-DD hoặc DD/MM/YYYY)
                    expiry_str = row.get('expiry_date', '')
                    if '/' in expiry_str:  # DD/MM/YYYY
                        expiry_date = datetime.strptime(expiry_str, '%d/%m/%Y')
                    else:  # YYYY-MM-DD
                        expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                    
                    expiry_date = timezone.make_aware(expiry_date)

                    Coupon.objects.update_or_create(
                        code=row['code'],
                        platform=platform,
                        defaults={
                            'title': row['title'],
                            'description': row.get('description', ''),
                            'discount_value': row['discount_value'],
                            'min_order_value': float(row.get('min_order_value', 0)),
                            'quota': int(row.get('quota', 0)) if row.get('quota') else None,
                            'expiry_date': expiry_date,
                            'status': 'approved',
                            'created_by': admin,
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing Shopee row: {e}'))

        self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} Shopee coupons'))

    def import_lazada(self, file_path, admin):
        """Import Lazada coupons from CSV"""
        platform = Platform.objects.get(name='Lazada')
        count = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expiry_str = row.get('expiry_date', '')
                    if '/' in expiry_str:
                        expiry_date = datetime.strptime(expiry_str, '%d/%m/%Y')
                    else:
                        expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                    
                    expiry_date = timezone.make_aware(expiry_date)

                    Coupon.objects.update_or_create(
                        code=row['code'],
                        platform=platform,
                        defaults={
                            'title': row['title'],
                            'description': row.get('description', ''),
                            'discount_value': row['discount_value'],
                            'min_order_value': float(row.get('min_order_value', 0)),
                            'quota': int(row.get('quota', 0)) if row.get('quota') else None,
                            'expiry_date': expiry_date,
                            'status': 'approved',
                            'created_by': admin,
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing Lazada row: {e}'))

        self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} Lazada coupons'))

    def import_tiktok(self, file_path, admin):
        """Import TikTok coupons from CSV"""
        platform = Platform.objects.get(name='TikTok Shop')
        count = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expiry_str = row.get('expiry_date', '')
                    if '/' in expiry_str:
                        expiry_date = datetime.strptime(expiry_str, '%d/%m/%Y')
                    else:
                        expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                    
                    expiry_date = timezone.make_aware(expiry_date)

                    Coupon.objects.update_or_create(
                        code=row['code'],
                        platform=platform,
                        defaults={
                            'title': row['title'],
                            'description': row.get('description', ''),
                            'discount_value': row['discount_value'],
                            'min_order_value': float(row.get('min_order_value', 0)),
                            'quota': int(row.get('quota', 0)) if row.get('quota') else None,
                            'expiry_date': expiry_date,
                            'status': 'approved',
                            'created_by': admin,
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing TikTok row: {e}'))

        self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} TikTok coupons'))