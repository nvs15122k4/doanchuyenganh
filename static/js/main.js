// JavaScript chung cho toàn bộ CouponHub

/**
 * Lấy CSRF token từ cookie (dùng chung cho tất cả AJAX request)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Copy mã giảm giá đơn giản (dùng cho saved_coupons, coupon_detail, all_coupons)
 */
function copyCode(code) {
    navigator.clipboard.writeText(code).then(function() {
        alert('✅ Đã sao chép mã: ' + code);
    }, function() {
        alert('❌ Không thể sao chép mã');
    });
}

/**
 * Copy mã và tăng view count (dùng cho home, coupons_list)
 */
function copyAndCount(code, couponId) {
    if (!code) {
        alert('Không có mã để sao chép');
        return;
    }
    
    // Copy mã
    navigator.clipboard.writeText(code)
        .then(() => {
            alert('✅ Đã sao chép mã: ' + code);
            
            // Tăng view count
            fetch(`/coupon/${couponId}/view/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
        })
        .catch(() => alert('❌ Không thể sao chép mã'));
}

/**
 * Sử dụng mã giảm giá ngay (dùng cho home, coupons_list)
 */
function useNow(couponId) {
    if (!confirm('Xác nhận sử dụng mã giảm giá này?')) {
        return;
    }
    
    fetch(`/coupon/${couponId}/use/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ ' + data.message);
            if (data.quota !== null) {
                alert('Còn lại: ' + data.quota + ' mã');
            }
            location.reload();
        } else {
            alert('⚠️ ' + data.message);
        }
    })
    .catch(error => {
        alert('❌ Có lỗi xảy ra');
        console.error(error);
    });
}

/**
 * Auto reload form sau khi submit (dùng cho sync_supabase, sync_external_api)
 */
document.addEventListener('DOMContentLoaded', function() {
    // Tự động reload form sau khi submit
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang xử lý...';
            }
        });
    });
});
