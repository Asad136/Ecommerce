from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/', views.create_store, name='create_store'),
    path('list/', views.store_list, name='store_list'),
    path('update/<int:pk>/', views.update_store, name='update_store'),
    path('delete/<int:pk>/', views.delete_store, name='delete_store'),
    path('<int:pk>/', views.store_detail, name='store_detail'),
    path('<int:store_id>/products/', views.product_list, name='product_list'),
    path('store/<int:store_id>/products/<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:store_id>/products/create/', views.create_product, name='create_product'),
    path('<int:store_id>/products/<int:pk>/update/', views.update_product, name='update_product'),
    path('<int:store_id>/products/<int:pk>/delete/', views.delete_product, name='delete_product'),


    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('order-success/', views.order_success, name='order_success'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:store_id>/product_analytics/', views.product_analytics, name='product_analytics'),
    path('verify-sellers/', views.verify_sellers, name='verify_sellers'),
    path('seller/product-stock/', views.seller_product_stock, name='seller_product_stock'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)