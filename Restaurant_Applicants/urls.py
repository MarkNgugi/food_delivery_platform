from django.urls import path
from . import views

app_name = 'restaurant_applicants'

urlpatterns = [

    path('dashboard/',
         views.dashboard,
         name='dashboard'
         ),

    path('applications/', 
         views.applications, 
         name='applications'
         ),

    path('applications/add/', 
         views.add_application, 
         name='add_application'
         ),

    path('my-restaurants/',
         views.my_restaurants,
         name='my_restaurants'
         ),

    path('my-restaurants/<int:restaurant_id>/',
         views.manage_restaurant,
         name='manage_restaurant'),

    path(
        'restaurants/<int:restaurant_id>/edit/',
        views.edit_restaurant,
        name='edit_restaurant'
    ),         

    path(
        'restaurants/<int:restaurant_id>/menu/add/',
        views.add_menu_item,
        name='add_menu_item'
    ),
]