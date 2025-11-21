from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Coupon, Platform, Category, UserSavedCoupon, User, SupportTicket
from .forms import CouponForm, LoginForm, RegisterForm, SupportTicketForm
from .services.supabase_service import SupabaseService
from .services.lazada_api import LazadaAPIClient
from .services.shopee_api import ShopeeAPIClient
from .services.tiktok_api import TikTokShopAPIClient


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def home(request):
    platforms = Platform.objects.all()
    search_query = request.GET.get('search', '')
    platform_filter = request.GET.get('platform', '')
    
    coupons = Coupon.objects.filter(
        status='approved',
        expiry_date__gt=timezone.now()
    )
    
    if search_query:
        coupons = coupons.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Lấy mã affiliate nổi bật (hiển thị đầu tiên)
    featured_coupons = coupons.filter(is_featured=True)[:3]
    
    # Nếu có filter platform
    if platform_filter:
        coupons = coupons.filter(platform_id=platform_filter)
        coupons = coupons.order_by('-is_featured', '-priority_score', '-view_count', '-use_count')
        
        # Pagination: 12 mã/trang
        paginator = Paginator(coupons, 12)
        page_obj = paginator.get_page(request.GET.get('page'))
        
        context = {
            'page_obj': page_obj,
            'featured_coupons': featured_coupons,
            'platforms': platforms,
            'search_query': search_query,
            'platform_filter': platform_filter,
            'show_pagination': True,
        }
    else:
        # Trang chủ: Lấy 12 mã HOT (4 mã/sàn)
        hot_coupons = []
        for platform in platforms:
            platform_coupons = coupons.filter(platform=platform).order_by(
                '-is_featured', '-priority_score', '-view_count', '-use_count'
            )[:4]
            hot_coupons.extend(platform_coupons)
        
        context = {
            'coupons': hot_coupons[:12],
            'featured_coupons': featured_coupons,
            'platforms': platforms,
            'search_query': search_query,
            'platform_filter': platform_filter,
            'show_pagination': False,
        }
    
    return render(request, 'coupons/home.html', context)


def coupon_detail(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    is_saved = False
    
    if request.user.is_authenticated:
        is_saved = UserSavedCoupon.objects.filter(
            user=request.user,
            coupon=coupon
        ).exists()
    
    context = {
        'coupon': coupon,
        'is_saved': is_saved,
    }
    return render(request, 'coupons/coupon_detail.html', context)


@login_required
def saved_coupons(request):
    saved_coupons_list = UserSavedCoupon.objects.filter(
        user=request.user
    ).select_related('coupon', 'coupon__platform').order_by('-saved_at')
    
    return render(request, 'coupons/saved_coupons.html', {'saved_coupons': saved_coupons_list})


@login_required
def save_coupon(request, coupon_id):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, pk=coupon_id)
        saved_coupon, created = UserSavedCoupon.objects.get_or_create(
            user=request.user,
            coupon=coupon
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Đã lưu mã thành công!'})
        return JsonResponse({'success': False, 'message': 'Mã đã được lưu trước đó!'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


@login_required
def unsave_coupon(request, coupon_id):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, pk=coupon_id)
        deleted = UserSavedCoupon.objects.filter(
            user=request.user,
            coupon=coupon
        ).delete()
        
        if deleted[0] > 0:
            return JsonResponse({'success': True, 'message': 'Đã bỏ lưu mã!'})
        return JsonResponse({'success': False, 'message': 'Mã chưa được lưu!'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('coupons:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng trở lại, {user.email}!')
                next_url = request.GET.get('next', 'coupons:home')
                return redirect(next_url)
            messages.error(request, 'Email hoặc mật khẩu không đúng!')
    else:
        form = LoginForm()
    
    return render(request, 'coupons/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('coupons:home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email này đã được sử dụng!')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='user'
                )
                login(request, user)
                messages.success(request, 'Đăng ký thành công!')
                return redirect('coupons:home')
    else:
        form = RegisterForm()
    
    return render(request, 'coupons/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Đã đăng xuất thành công!')
    return redirect('coupons:home')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        'total_coupons': Coupon.objects.count(),
        'approved_coupons': Coupon.objects.filter(status='approved').count(),
        'pending_coupons': Coupon.objects.filter(status='pending').count(),
        'expired_coupons': Coupon.objects.filter(status='expired').count(),
        'total_users': User.objects.filter(role='user').count(),
    }
    return render(request, 'coupons/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_coupon_list(request):
    platform_filter = request.GET.get('platform', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    coupons = Coupon.objects.all().select_related('platform', 'created_by')
    
    if platform_filter:
        coupons = coupons.filter(platform_id=platform_filter)
    if status_filter:
        coupons = coupons.filter(status=status_filter)
    if search_query:
        coupons = coupons.filter(
            Q(code__icontains=search_query) |
            Q(title__icontains=search_query)
        )
    
    paginator = Paginator(coupons, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'platforms': Platform.objects.all(),
        'platform_filter': platform_filter,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'coupons/admin/coupon_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_coupon_create(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user
            coupon.save()
            form.save_m2m()
            messages.success(request, 'Đã tạo mã giảm giá thành công!')
            return redirect('coupons:admin_coupon_list')
    else:
        form = CouponForm()
    
    return render(request, 'coupons/admin/coupon_form.html', {'form': form, 'title': 'Thêm mã mới'})


@login_required
@user_passes_test(is_admin)
def admin_coupon_edit(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật mã giảm giá thành công!')
            return redirect('coupons:admin_coupon_list')
    else:
        form = CouponForm(instance=coupon)
    
    return render(request, 'coupons/admin/coupon_form.html', {'form': form, 'coupon': coupon, 'title': 'Sửa mã'})


@login_required
@user_passes_test(is_admin)
def admin_coupon_delete(request, coupon_id):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, pk=coupon_id)
        coupon.delete()
        messages.success(request, 'Đã xóa mã giảm giá thành công!')
    return redirect('coupons:admin_coupon_list')


@login_required
@user_passes_test(is_admin)
def admin_platform_list(request):
    return render(request, 'coupons/admin/platform_list.html', {'platforms': Platform.objects.all()})


@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.filter(role='user').order_by('-created_at')
    return render(request, 'coupons/admin/user_list.html', {'users': users})


@login_required
def supabase_coupons_api(request):
    limit = int(request.GET.get('limit', 20))
    data = SupabaseService().fetch_coupons(limit=limit)
    return JsonResponse({'coupons': data})


@login_required
@user_passes_test(is_admin)
def admin_external_vouchers(request):
    response_data = {
        'lazada': {'status': 'disabled', 'data': []},
        'shopee': {'status': 'disabled', 'data': []},
        'tiktok': {'status': 'disabled', 'data': []},
    }

    lazada_client = LazadaAPIClient()
    if lazada_client.is_configured():
        response_data['lazada'] = {
            'status': 'ok',
            'data': lazada_client.get_vouchers(page_size=10),
        }

    shopee_client = ShopeeAPIClient()
    if shopee_client.is_configured():
        response_data['shopee'] = {
            'status': 'ok',
            'data': shopee_client.get_vouchers(page_size=10),
        }

    tiktok_client = TikTokShopAPIClient()
    if tiktok_client.is_configured():
        response_data['tiktok'] = {
            'status': 'ok',
            'data': tiktok_client.get_seller_vouchers(page_size=10),
        }

    return JsonResponse(response_data)



def coupons_list(request):
    platform_filter = request.GET.get('platform', '')
    sort_by = request.GET.get('sort', '-created_at')
    search_query = request.GET.get('search', '')
    
    coupons = Coupon.objects.filter(
        status='approved',
        expiry_date__gt=timezone.now()
    ).select_related('platform')
    
    if platform_filter:
        coupons = coupons.filter(platform_id=platform_filter)
    
    if search_query:
        coupons = coupons.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if sort_by == 'discount_high':
        coupons = coupons.order_by('-is_featured', '-priority_score', '-min_order_value')
    elif sort_by == 'discount_low':
        coupons = coupons.order_by('-is_featured', '-priority_score', 'min_order_value')
    elif sort_by == 'quota_high':
        coupons = coupons.order_by('-is_featured', '-priority_score', '-quota')
    elif sort_by == 'quota_low':
        coupons = coupons.order_by('-is_featured', '-priority_score', 'quota')
    elif sort_by == 'popular':
        coupons = coupons.order_by('-is_featured', '-priority_score', '-view_count', '-use_count')
    else:
        coupons = coupons.order_by('-is_featured', '-priority_score', '-created_at')
    
    # Pagination: 12 mã/trang
    paginator = Paginator(coupons, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'platforms': Platform.objects.all(),
        'platform_filter': platform_filter,
        'sort_by': sort_by,
        'search_query': search_query,
    }
    
    return render(request, 'coupons/coupons_list.html', context)


@login_required
def support_create(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            messages.success(request, f'Ticket #{ticket.ticket_id} đã được gửi thành công!')
            return redirect('coupons:support_list')
    else:
        form = SupportTicketForm()
    
    return render(request, 'coupons/support_create.html', {'form': form})


@login_required
def support_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'coupons/support_list.html', {'tickets': tickets})


@login_required
def support_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, user=request.user)
    return render(request, 'coupons/support_detail.html', {'ticket': ticket})
