#!/usr/bin/env python
"""
Script tạo Django SECRET_KEY mới
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    print("=" * 60)
    print("🔑 DJANGO SECRET KEY MỚI")
    print("=" * 60)
    print()
    print(get_random_secret_key())
    print()
    print("📝 Copy key này và thêm vào biến môi trường:")
    print("   DJANGO_SECRET_KEY=<key-ở-trên>")
    print("=" * 60)
