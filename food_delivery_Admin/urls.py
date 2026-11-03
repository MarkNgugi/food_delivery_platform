from django.urls import path
from . import views

app_name = 'food_delivery_Admin'

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard')
]