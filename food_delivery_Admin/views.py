from django.shortcuts import render
from . import views

def dashboard(request):

    return render(request,'food_delivery_Admin/base.html')
