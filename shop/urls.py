from django.urls import path
from shop import views

urlpatterns = [
    path('categories/', views.get_categories, name='get_categories'),
    path('products/<int:pk>/', views.get_products, name='get_products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.get_cart_list, name='get_cart_list'),
    path('cart/add/', views.add_cart_item, name='add_cart_item'),
    path('cart/merge/', views.merge_cart, name='merge_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/', views.delete_cart_item, name='delete_cart_item'),
    # path('cart/<int:pk>/', views.CartItemRetrieveUpdateDelete.as_view(), name='cartitemupdatedelete'),
]