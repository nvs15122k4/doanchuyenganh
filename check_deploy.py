#!/usr/bin/env python
"""
Script kiểm tra cấu hình trước khi deploy
"""
import os
import sys

def check_requirements():
    """Kiểm tra file requirements.txt"""
    required_packages = [
        'Django',
        'gunicorn',
        'whitenoise',
        'dj-database-url'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            missing = []
            for pkg in required_packages:
                if pkg.lower() not in content.lower():
                    missing.append(pkg)
            
            if missing:
                print(f"❌ Thiếu packages: {', '.join(missing)}")
                return False
            else:
                print("✅ requirements.txt OK")
                return True
    except FileNotFoundError:
        print("❌ Không tìm thấy requirements.txt")
        return False

def check_procfile():
    """Kiểm tra Procfile"""
    if os.path.exists('Procfile'):
        print("✅ Procfile OK")
        return True
    else:
        print("❌ Không tìm thấy Procfile")
        return False

def check_runtime():
    """Kiểm tra runtime.txt"""
    if os.path.exists('runtime.txt'):
        print("✅ runtime.txt OK")
        return True
    else:
        print("⚠️  Không có runtime.txt (không bắt buộc)")
        return True

def check_settings():
    """Kiểm tra settings.py"""
    try:
        with open('CouponHub/settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            checks = {
                'whitenoise': 'whitenoise' in content.lower(),
                'dj_database_url': 'dj_database_url' in content or 'dj-database-url' in content,
                'allowed_hosts': 'ALLOWED_HOSTS' in content,
                'static_root': 'STATIC_ROOT' in content,
            }
            
            all_ok = True
            for check, result in checks.items():
                if result:
                    print(f"✅ settings.py - {check} OK")
                else:
                    print(f"❌ settings.py - thiếu {check}")
                    all_ok = False
            
            return all_ok
    except FileNotFoundError:
        print("❌ Không tìm thấy settings.py")
        return False

def check_gitignore():
    """Kiểm tra .gitignore"""
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if '.env' in content and 'db.sqlite3' in content:
                print("✅ .gitignore OK")
                return True
            else:
                print("⚠️  .gitignore thiếu .env hoặc db.sqlite3")
                return True
    else:
        print("⚠️  Không có .gitignore")
        return True

def check_env_example():
    """Kiểm tra .env.example"""
    if os.path.exists('.env.example'):
        print("✅ .env.example OK")
        return True
    else:
        print("⚠️  Không có .env.example (nên có)")
        return True

def main():
    print("=" * 50)
    print("🔍 KIỂM TRA CẤU HÌNH DEPLOY")
    print("=" * 50)
    print()
    
    checks = [
        check_requirements(),
        check_procfile(),
        check_runtime(),
        check_settings(),
        check_gitignore(),
        check_env_example(),
    ]
    
    print()
    print("=" * 50)
    if all(checks):
        print("✅ TẤT CẢ KIỂM TRA PASS - SẴN SÀNG DEPLOY!")
    else:
        print("❌ CÓ LỖI - VUI LÒNG SỬA TRƯỚC KHI DEPLOY")
    print("=" * 50)
    print()
    print("📖 Xem hướng dẫn chi tiết trong DEPLOY.md")
    
    return 0 if all(checks) else 1

if __name__ == '__main__':
    sys.exit(main())
