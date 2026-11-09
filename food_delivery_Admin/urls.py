from django.urls import path
from . import views

app_name = 'food_delivery_Admin'

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard'),

    path('restaurants/',views.restaurants, name='restaurants'),


    path(
        'restaurants/<int:restaurant_id>/',
        views.restaurant_detail,
        name='restaurant_detail',
    ),

    path(
        'restaurants/<int:restaurant_id>/edit/',
        views.restaurant_edit,
        name='restaurant_edit',
    ),

    path(
        'restaurants/<int:restaurant_id>/delete/',
        views.restaurant_delete,
        name='restaurant_delete',
    ),

    path('orders',views.orders,name='orders'),

    path(
    'menu-management',
    views.menu_management,
    name='menu_management'
),

    path('customers',views.customers,name='customers'),

    path('delivery-management',views.delivery_management,name='delivery_management'),

    path('restaurant-owners',views.restaurant_owners,name='restaurant_owners'),

    path(
    'cuisine-categories/',
    views.cuisine_categories,
    name='cuisine_categories'
),

    path('reports-analytics/', views.reports_analytics, name='reports_analytics'),
    
    path('settings/', views.admin_settings, name='settings'),
]