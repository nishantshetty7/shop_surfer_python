from django.urls import path
from .views import LoginUserView, LoginRefreshView, register, logout, send_email, verify_register, resend_register, google_login, email_verification

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login_refresh'),
    path('google/login/', google_login, name='google_login'),
    path('logout/', logout, name='logout'),
    path('email/', send_email, name='send_email'),
    path('verify/register/', verify_register, name='verify_register'),
    path('resend/register/', resend_register, name='resend_register'),
    path('email_verification/', email_verification, name='email_verification'),
]