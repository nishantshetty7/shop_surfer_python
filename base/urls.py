from django.urls import path
from .views import LoginUserView, LoginRefreshView, register, logout

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login_refresh'),
    path('logout/', logout, name='logout'),
]