from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.db.models import Q

from food_delivery.models import Restaurant
from food_delivery.forms import RestaurantRegistrationForm


def dashboard(request):
    restaurants = (
        Restaurant.objects
        .filter(owner=request.user)
        .select_related('cuisine')
        .prefetch_related('operating_hours')
        .order_by('-created_at')
    )

    restaurant = restaurants.first()

    context = {
        'restaurant': restaurant,
        'restaurant_count': restaurants.count(),
        'user': request.user,
    }

    return render(
        request,
        'Restaurant_Applicants/dashboard.html',
        context
    )


def applications(request):
    restaurant_applications = Restaurant.objects.filter(
        owner=request.user
    ).select_related('cuisine').order_by('-created_at')

    context = {
        'applications': restaurant_applications,
        'total_applications': restaurant_applications.count(),
        'pending_count': restaurant_applications.filter(status='pending').count(),
        'approved_count': restaurant_applications.filter(status='approved').count(),
        'rejected_count': restaurant_applications.filter(status='rejected').count(),
        'suspended_count': restaurant_applications.filter(status='suspended').count(),
    }

    return render(
        request,
        'Restaurant_Applicants/applications/applications.html',
        context
    )


def add_application(request):

    if request.method == 'POST':
        form = RestaurantRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                restaurant = form.save(commit=False)
                restaurant.owner = request.user
                restaurant.status = 'pending'
                restaurant.save()

            messages.success(
                request,
                'Your restaurant application has been submitted successfully!'
            )

            return redirect('restaurant_applicants:applications')

    else:
        form = RestaurantRegistrationForm()

    return render(
        request,
        'Restaurant_Applicants/applications/application_form.html',
        {'form': form}
    )










def my_restaurants(request):
    restaurants = (
        Restaurant.objects
        .filter(owner=request.user)
        .select_related('cuisine')
        .order_by('-created_at')
    )

    total_restaurants = restaurants.count()
    approved_restaurants = restaurants.filter(status='approved').count()
    pending_restaurants = restaurants.filter(status='pending').count()

    needs_attention = restaurants.filter(
        status__in=['rejected', 'suspended']
    ).count()

    context = {
        'restaurants': restaurants,
        'total_restaurants': total_restaurants,
        'approved_restaurants': approved_restaurants,
        'pending_restaurants': pending_restaurants,
        'needs_attention': needs_attention,
    }

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/my_restaurants.html',
        context
    )


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404



@login_required
def manage_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user,
        status='approved'
    )

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/manage_restaurant.html',
        {'restaurant': restaurant}
    )
