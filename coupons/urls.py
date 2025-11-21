from django.urls import path
from . import views
from . import api_views
from . import admin_views
from . import coupon_actions

app_name = 'coupons'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('coupons/', views.coupons_list, name='coupons_list'),
    path('coupon/<int:coupon_id>/', views.coupon_detail, name='coupon_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # User pages
    path('saved/', views.saved_coupons, name='saved_coupons'),
    path('save/<int:coupon_id>/', views.save_coupon, name='save_coupon'),
    path('unsave/<int:coupon_id>/', views.unsave_coupon, name='unsave_coupon'),
    
    # Support pages
    path('support/', views.support_create, name='support_create'),
    path('support/list/', views.support_list, name='support_list'),
    path('support/<int:ticket_id>/', views.support_detail, name='support_detail'),
    
    # Admin pages
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/stats/users/', admin_views.admin_user_stats, name='admin_user_stats'),
    path('admin/coupons/', views.admin_coupon_list, name='admin_coupon_list'),
    path('admin/coupons/create/', views.admin_coupon_create, name='admin_coupon_create'),
    path('admin/coupons/<int:coupon_id>/edit/', views.admin_coupon_edit, name='admin_coupon_edit'),
    path('admin/coupons/<int:coupon_id>/delete/', views.admin_coupon_delete, name='admin_coupon_delete'),
    path('admin/platforms/', views.admin_platform_list, name='admin_platform_list'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/integrations/vouchers/', views.admin_external_vouchers, name='admin_external_vouchers'),
    path('admin/support/', admin_views.admin_support_tickets, name='admin_support_tickets'),
    path('admin/support/<int:ticket_id>/', admin_views.admin_support_detail, name='admin_support_detail'),
    path('admin/sync-supabase/', admin_views.admin_sync_supabase, name='admin_sync_supabase'),
    
    # Coupon actions
    path('coupon/<int:coupon_id>/view/', coupon_actions.increment_view_count, name='increment_view'),
    path('coupon/<int:coupon_id>/use/', coupon_actions.increment_use_count, name='increment_use'),
    
    # API endpoints
    path('api/coupons/', api_views.api_coupons_list, name='api_coupons_list'),
    path('api/coupons/<int:coupon_id>/', api_views.api_coupon_detail, name='api_coupon_detail'),
    path('api/platforms/', api_views.api_platforms_list, name='api_platforms_list'),
    path('api/supabase/coupons/', views.supabase_coupons_api, name='supabase_coupons_api'),
]

