"""
Coupon actions - View, Use, Save
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import Coupon
import time

def increment_view_count(request, coupon_id):
    """Tăng view count với rate limiting"""
    coupon = get_object_or_404(Coupon, coupon_id=coupon_id)
    
    # Rate limiting: 1 view mỗi 10 giây cho mỗi IP + coupon
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'view_{ip}_{coupon_id}'
    
    if not cache.get(cache_key):
        coupon.view_count += 1
        coupon.save(update_fields=['view_count'])
        cache.set(cache_key, True, 10)  # 10 giây
        
        return JsonResponse({
            'success': True,
            'view_count': coupon.view_count
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Vui lòng đợi 10 giây'
    })


@require_POST
def increment_use_count(request, coupon_id):
    """Tăng use count và giảm quota"""
    coupon = get_object_or_404(Coupon, coupon_id=coupon_id)
    
    # Rate limiting: 1 use mỗi 30 giây cho mỗi IP + coupon
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f'use_{ip}_{coupon_id}'
    
    if cache.get(cache_key):
        return JsonResponse({
            'success': False,
            'message': 'Bạn vừa sử dụng mã này. Vui lòng đợi 30 giây.'
        })
    
    # Kiểm tra quota
    if coupon.quota is not None and coupon.quota <= 0:
        return JsonResponse({
            'success': False,
            'message': 'Mã giảm giá đã hết lượt sử dụng!'
        })
    
    # Tăng use count và giảm quota
    coupon.use_count += 1
    if coupon.quota is not None:
        coupon.quota -= 1
    coupon.save(update_fields=['use_count', 'quota'])
    
    # Set cache 30 giây
    cache.set(cache_key, True, 30)
    
    return JsonResponse({
        'success': True,
        'use_count': coupon.use_count,
        'quota': coupon.quota,
        'message': f'Đã sử dụng mã {coupon.code}!'
    })
