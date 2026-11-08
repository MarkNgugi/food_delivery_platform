from django.urls import path
from . import views

app_name = 'food_delivery_Admin'

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard'),

    path('restaurants/',views.restaurants, name='restaurants'),

    path('orders',views.orders,name='orders'),

    path('menu-management',views.menu_management,name='menu_management'),

    path('customers',views.customers,name='customers'),

    path('delivery-management',views.delivery_management,name='delivery_management'),
]