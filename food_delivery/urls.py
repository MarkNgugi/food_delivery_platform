from django.urls import path
from . import views


urlpatterns = [

    path(
        'restaurant/register/',
        views.restaurant_register,
        name='restaurant_register'
    ),

    path(
        'restaurant/<int:pk>/profile/',
        views.restaurant_profile,
        name='restaurant_profile'
    ),

    path(
        'restaurant/<int:pk>/operating-hours/',
        views.restaurant_operating_hours,
        name='restaurant_operating_hours'
    ),

]
