from django import forms
from .models import Coupon, Platform, Category, User, APIConfiguration


class CouponForm(forms.ModelForm):
    expiry_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )

    class Meta:
        model = Coupon
        fields = [
            'platform', 'code', 'title', 'description',
            'discount_value', 'min_order_value', 'quota',
            'expiry_date', 'affiliate_link', 'status', 'categories',
            'is_affiliate', 'affiliate_commission', 'priority_score', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'discount_value': forms.TextInput(attrs={'placeholder': 'VD: 50%, 100K, 200đ'}),
            'categories': forms.CheckboxSelectMultiple(),
            'is_affiliate': forms.CheckboxInput(attrs={'class': 'w-4 h-4'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4'}),
            'affiliate_commission': forms.TextInput(attrs={'placeholder': 'VD: 5.5%, 50đ, 100K'}),
            'priority_score': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
        }
        help_texts = {
            'is_affiliate': '✅ Đánh dấu là mã tiếp thị liên kết',
            'affiliate_commission': 'Hoa hồng (có thể dùng %, đ, K)',
            'priority_score': 'Điểm ưu tiên (0-100, càng cao càng ưu tiên)',
            'is_featured': '⭐ Hiển thị trong mục nổi bật',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['platform'].queryset = Platform.objects.all()
        self.fields['categories'].queryset = Category.objects.all()


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Email của bạn'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Mật khẩu'
        })
    )


class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Email của bạn'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Tên người dùng'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Mật khẩu'
        })
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Xác nhận mật khẩu'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Mật khẩu không khớp!")

        return cleaned_data




class SupportTicketForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Tiêu đề vấn đề của bạn'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Mô tả chi tiết vấn đề...',
            'rows': 6
        })
    )


class APIConfigurationForm(forms.ModelForm):
    class Meta:
        model = APIConfiguration
        fields = ['platform', 'api_url', 'api_key', 'is_active']
        widgets = {
            'platform': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'api_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://api.example.com/vouchers'
            }),
            'api_key': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nhập API Key hoặc Access Token'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500'
            }),
        }
