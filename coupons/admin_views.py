from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .decorators import admin_required
from .models import Coupon, User, Platform, SupportTicket


@admin_required
def admin_dashboard(request):
    view_sum = Coupon.objects.aggregate(Sum('view_count'))
    use_sum = Coupon.objects.aggregate(Sum('use_count'))
    
    total_views = view_sum['view_count__sum'] or 0
    total_uses = use_sum['use_count__sum'] or 0
    
    top_viewed = Coupon.objects.select_related('platform').order_by('-view_count')[:10]
    top_used = Coupon.objects.select_related('platform').order_by('-use_count')[:10]
    
    platform_stats = Platform.objects.annotate(
        total_coupons=Count('coupons'),
        active_coupons=Count('coupons', filter=Q(
            coupons__status='approved',
            coupons__expiry_date__gt=timezone.now()
        )),
        total_views=Sum('coupons__view_count'),
        total_uses=Sum('coupons__use_count')
    ).order_by('-total_coupons')
    
    context = {
        'total_users': User.objects.filter(role='user').count(),
        'total_coupons': Coupon.objects.count(),
        'active_coupons': Coupon.objects.filter(status='approved', expiry_date__gt=timezone.now()).count(),
        'expired_coupons': Coupon.objects.filter(Q(status='expired') | Q(expiry_date__lte=timezone.now())).count(),
        'total_views': total_views,
        'total_uses': total_uses,
        'top_viewed': top_viewed,
        'top_used': top_used,
        'platform_stats': platform_stats,
    }
    
    return render(request, 'coupons/admin/dashboard.html', context)





@admin_required
def admin_user_stats(request):
    users = User.objects.filter(role='user').annotate(
        saved_count=Count('saved_coupons')
    ).order_by('-date_joined')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'users_with_saved': users.filter(saved_count__gt=0).count(),
    }
    
    return render(request, 'coupons/admin/user_stats.html', context)



@admin_required
def admin_support_tickets(request):
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    tickets = SupportTicket.objects.select_related('user', 'responded_by').all()
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    tickets = tickets.order_by('-created_at')
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'total_tickets': SupportTicket.objects.count(),
        'open_tickets': SupportTicket.objects.filter(status='open').count(),
        'in_progress_tickets': SupportTicket.objects.filter(status='in_progress').count(),
        'resolved_tickets': SupportTicket.objects.filter(status='resolved').count(),
    }
    
    return render(request, 'coupons/admin/support_tickets.html', context)


@admin_required
def admin_support_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            ticket.status = new_status
            if new_status == 'resolved':
                ticket.resolved_at = timezone.now()
            ticket.save()
            messages.success(request, 'Cập nhật trạng thái thành công!')
        
        elif action == 'update_priority':
            ticket.priority = request.POST.get('priority')
            ticket.save()
            messages.success(request, 'Cập nhật độ ưu tiên thành công!')
        
        elif action == 'respond':
            response = request.POST.get('response')
            if response:
                ticket.admin_response = response
                ticket.responded_by = request.user
                ticket.status = 'in_progress'
                ticket.save()
                messages.success(request, 'Phản hồi đã được gửi!')
        
        return redirect('coupons:admin_support_detail', ticket_id=ticket_id)
    
    return render(request, 'coupons/admin/support_detail.html', {'ticket': ticket})



@admin_required
def admin_sync_supabase(request):
    """Trang đồng bộ mã từ API các sàn TMĐT"""
    from django.conf import settings
    import requests
    from datetime import datetime
    from .models import APIConfiguration
    from .forms import APIConfigurationForm
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_config':
            platform = request.POST.get('platform')
            api_url = request.POST.get('api_url', '').strip()
            api_key = request.POST.get('api_key', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            config, created = APIConfiguration.objects.update_or_create(
                platform=platform,
                defaults={
                    'api_url': api_url,
                    'api_key': api_key,
                    'is_active': is_active
                }
            )
            
            action_text = "Tạo mới" if created else "Cập nhật"
            messages.success(request, f'{action_text} cấu hình API {config.get_platform_display()} thành công!')
            return redirect('coupons:admin_sync_supabase')
        
        elif action == 'sync':
            platform_table = request.POST.get('platform_table')
            platform_name = request.POST.get('platform_name')
            platform_key = request.POST.get('platform_key')
            
            try:
                api_config = APIConfiguration.objects.get(platform=platform_key, is_active=True)
            except APIConfiguration.DoesNotExist:
                messages.error(request, f'Chưa cấu hình API cho {platform_name}. Vui lòng cấu hình trước.')
                return redirect('coupons:admin_sync_supabase')
            
            api_url = api_config.api_url
            api_key = api_config.api_key
            
            try:
                platform = Platform.objects.get(name=platform_name)
                
                headers = {
                    "apikey": api_key,
                    "Authorization": f"Bearer {api_key}"
                }
                
                # Xử lý URL: nếu đã có /rest/v1 thì không thêm nữa
                if '/rest/v1/' in api_url:
                    url = f"{api_url.rstrip('/')}/{platform_table}"
                else:
                    url = f"{api_url.rstrip('/')}/rest/v1/{platform_table}"
                
                params = {"is_active": "eq.true"}
                
                # Thử kết nối API
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        coupons_data = response.json()
                    elif response.status_code == 401:
                        messages.error(request, f'API Key không hợp lệ cho {platform_name}. Vui lòng kiểm tra lại hoặc tạo Supabase project mới.')
                        return redirect('coupons:admin_sync_supabase')
                    else:
                        messages.error(request, f'Lỗi API {platform_name}: Status {response.status_code}')
                        return redirect('coupons:admin_sync_supabase')
                        
                except requests.exceptions.RequestException as e:
                    messages.error(request, f'Không thể kết nối đến API: {str(e)}')
                    return redirect('coupons:admin_sync_supabase')
                
                if coupons_data:
                    created_count = 0
                    updated_count = 0
                    error_count = 0
                    
                    for coupon_data in coupons_data:
                        try:
                            expiry_date_str = coupon_data['expiry_date'].replace('Z', '+00:00')
                            expiry_date = datetime.fromisoformat(expiry_date_str)
                            
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
                            else:
                                updated_count += 1
                        except Exception as e:
                            error_count += 1
                            print(f"Error syncing coupon: {e}")
                    
                    api_config.last_sync = timezone.now()
                    api_config.save()
                    
                    messages.success(
                        request, 
                        f'Đồng bộ {platform_name} thành công! Tạo mới: {created_count}, Cập nhật: {updated_count}, Lỗi: {error_count}'
                    )
                else:
                    error_detail = f'Status: {response.status_code}'
                    try:
                        error_json = response.json()
                        if 'message' in error_json:
                            error_detail += f' - {error_json["message"]}'
                    except:
                        pass
                    messages.error(request, f'Lỗi kết nối API {platform_name}: {error_detail}')
            
            except Platform.DoesNotExist:
                messages.error(request, f'Không tìm thấy platform: {platform_name}. Vui lòng tạo platform trong database.')
            except requests.exceptions.ConnectionError:
                messages.error(request, f'Không thể kết nối đến {api_url}. Kiểm tra lại URL và kết nối internet.')
            except requests.exceptions.Timeout:
                messages.error(request, f'Timeout khi kết nối API {platform_name}. Thử lại sau.')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Lỗi kết nối API: {str(e)}')
            except Exception as e:
                messages.error(request, f'Lỗi không xác định: {str(e)}')
            
            return redirect('coupons:admin_sync_supabase')
    
    from .models import APIConfiguration
    
    api_configs = {
        'shopee': APIConfiguration.objects.filter(platform='shopee').first(),
        'lazada': APIConfiguration.objects.filter(platform='lazada').first(),
        'tiktok': APIConfiguration.objects.filter(platform='tiktok').first(),
    }
    
    platforms_data = [
        {
            'name': 'Shopee',
            'key': 'shopee',
            'table': 'shopee_coupons', 
            'icon': 'fa-shopping-bag', 
            'color': 'orange',
            'default_api_url': 'https://api.shopee.vn/vouchers',
            'api_key_label': 'Shopee API Key',
            'config': api_configs['shopee']
        },
        {
            'name': 'Lazada',
            'key': 'lazada',
            'table': 'lazada_coupons', 
            'icon': 'fa-shopping-cart', 
            'color': 'blue',
            'default_api_url': 'https://api.lazada.com/vouchers',
            'api_key_label': 'Lazada App Key',
            'config': api_configs['lazada']
        },
        {
            'name': 'TikTok Shop',
            'key': 'tiktok',
            'table': 'tiktok_coupons', 
            'icon': 'fa-music', 
            'color': 'pink',
            'default_api_url': 'https://api.tiktokshop.com/vouchers',
            'api_key_label': 'TikTok API Token',
            'config': api_configs['tiktok']
        },
    ]
    
    stats = {
        'total_coupons': Coupon.objects.count(),
        'synced_coupons': Coupon.objects.filter(synced_from_api=True).count(),
        'shopee_count': Coupon.objects.filter(platform__name='Shopee').count(),
        'lazada_count': Coupon.objects.filter(platform__name='Lazada').count(),
        'tiktok_count': Coupon.objects.filter(platform__name='TikTok Shop').count(),
    }
    
    context = {
        'platforms_data': platforms_data,
        'stats': stats,
    }
    
    return render(request, 'coupons/admin/sync_external_api.html', context)
