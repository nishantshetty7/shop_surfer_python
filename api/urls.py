from django.urls import path
from . import views
from .views import CustomAuthTokenView, CustomRefreshTokenView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('', views.getRoutes),
    # path('notes/', views.getNotes),

    path('token/', CustomAuthTokenView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
]