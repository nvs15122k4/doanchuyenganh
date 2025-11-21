from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json
from .models import Coupon, Platform, UserSavedCoupon


@require_http_methods(["GET"])
def api_coupons_list(request):
    """API: Lấy danh sách mã giảm giá"""
    search = request.GET.get('search', '')
    platform_id = request.GET.get('platform', '')
    status = request.GET.get('status', 'approved')
    
    coupons = Coupon.objects.filter(status=status, expiry_date__gt=timezone.now())
    
    if search:
        coupons = coupons.filter(
            Q(title__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    if platform_id:
        coupons = coupons.filter(platform_id=platform_id)
    
    coupons = coupons.select_related('platform')[:50]
    
    data = [{
        'id': c.coupon_id,
        'code': c.code,
        'title': c.title,
        'description': c.description,
        'discount_value': c.discount_value,
        'min_order_value': str(c.min_order_value),
        'quota': c.quota,
        'expiry_date': c.expiry_date.isoformat(),
        'affiliate_link': c.affiliate_link,
        'platform': {
            'id': c.platform.platform_id,
            'name': c.platform.name,
            'logo_url': c.platform.logo_url,
        }
    } for c in coupons]
    
    return JsonResponse({'coupons': data}, safe=False)


@require_http_methods(["GET"])
def api_coupon_detail(request, coupon_id):
    """API: Lấy chi tiết một mã giảm giá"""
    try:
        coupon = Coupon.objects.select_related('platform').get(pk=coupon_id)
        data = {
            'id': coupon.coupon_id,
            'code': coupon.code,
            'title': coupon.title,
            'description': coupon.description,
            'discount_value': coupon.discount_value,
            'min_order_value': str(coupon.min_order_value),
            'quota': coupon.quota,
            'expiry_date': coupon.expiry_date.isoformat(),
            'affiliate_link': coupon.affiliate_link,
            'status': coupon.status,
            'platform': {
                'id': coupon.platform.platform_id,
                'name': coupon.platform.name,
                'logo_url': coupon.platform.logo_url,
            }
        }
        return JsonResponse(data)
    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'}, status=404)


@require_http_methods(["GET"])
def api_platforms_list(request):
    """API: Lấy danh sách sàn"""
    platforms = Platform.objects.all()
    data = [{
        'id': p.platform_id,
        'name': p.name,
        'logo_url': p.logo_url,
    } for p in platforms]
    
    return JsonResponse({'platforms': data}, safe=False)



