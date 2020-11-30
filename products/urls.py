from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_products, name='view_products'),
    path('<int:product_id>/', views.view_product, name='view_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add/', views.add_product, name='add_product'),
]
