from django.urls import path
from . import views

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
]