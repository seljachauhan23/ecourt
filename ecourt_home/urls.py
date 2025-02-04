from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('aboutus', aboutus, name='aboutus'),
    path('contactus', contactus, name='contactus'),
    path('terms-and-condition', terms_and_conditions, name='terms_and_condition'),
    path('privacy-policy', privacy_policy, name='privacy_policy'),
    path('faq', faq, name='faq'),
    path('dashboard', dashboard, name='dashboard'),
    path('logout',logout, name= 'logout'),
    path('signup/', signup, name='signup'),
    path('login', login_view, name='login'),
    path('login-with-otp', login_with_otp, name='login_with_otp'),
    path('login-with-otp/verify-otp', verify_login_otp, name='verify_login_otp'),
    path('resend-otp', resend_otp, name='resend_otp'),
    path('forgot-password', forgot_password, name='forgot_password'),
    path('forgot-password/verify-otp', verify_forgot_password_otp, name='verify_forgot_password_otp'),
    path('forgot-password/change-password', change_password, name='change_password'),
    path('page-not-found', error_404_view, name='error_404_view'),
    path('header-footer', header_footer, name='header_footer'),
    path('refund-cancellation/', refund_cancellation, name='refund_cancellation'),
]

handler400 = 'ecourt_home.views.error_404_view'
