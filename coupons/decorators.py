from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator yêu cầu user phải là admin.
    Redirect về home nếu không phải admin.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        print(f"DEBUG decorator: user={request.user.email}, role={request.user.role}, is_auth={request.user.is_authenticated}")
        
        if not request.user.is_authenticated:
            print("DEBUG: User not authenticated, redirecting to login")
            messages.error(request, '⛔ Vui lòng đăng nhập để tiếp tục!')
            return redirect('coupons:login')
        
        if request.user.role != 'admin':
            print(f"DEBUG: User role is '{request.user.role}', not 'admin', redirecting to home")
            messages.error(request, '⛔ Bạn không có quyền truy cập trang quản trị!')
            return redirect('coupons:home')
        
        print("DEBUG: User is admin, calling view")
        return view_func(request, *args, **kwargs)
    
    return wrapper
