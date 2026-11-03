from django.urls import path
from . import views


urlpatterns = [
    path(
        'home/',
        views.home,
        name='home'),

    path(
        'restaurant/register/',
        views.restaurant_register,
        name='restaurant_register'),

    path(
        'restaurant/<int:pk>/profile/',
        views.restaurant_profile,
        name='restaurant_profile'),

    path(
        'restaurant/<int:pk>/operating-hours/',
        views.restaurant_operating_hours,
        name='restaurant_operating_hours'),

    path(
        "restaurants/",
        views.restaurant_list,
        name="restaurant_list"
    ),
]
