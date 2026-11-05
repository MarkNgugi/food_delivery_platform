from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.http import require_POST

from food_delivery.models import Restaurant, MenuItem
from food_delivery.forms import RestaurantRegistrationForm, RestaurantUpdateForm, MenuItemForm




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



def manage_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user,
        status='approved'
    )

    # Get the restaurant's active menu items
    menu_items = (
        restaurant.menu_items
        .select_related('category')
        .filter(is_active=True)
        .order_by('-created_at')[:5]
    )

    # Count all active menu items
    active_menu_items_count = restaurant.menu_items.filter(
        is_active=True
    ).count()

    # Count the distinct categories used by active menu items
    menu_category_count = restaurant.menu_items.filter(
        is_active=True
    ).values('category_id').distinct().count()

    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'active_menu_items_count': active_menu_items_count,
        'menu_category_count': menu_category_count,
    }

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/manage_restaurant.html',
        context
    )


@login_required
def edit_restaurant(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user
    )

    if request.method == 'POST':
        form = RestaurantUpdateForm(
            request.POST,
            request.FILES,
            instance=restaurant
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your restaurant information has been updated successfully.'
            )

            return redirect(
                'restaurant_applicants:manage_restaurant',
                restaurant_id=restaurant.id
            )

        messages.error(
            request,
            'Please correct the errors below and try again.'
        )

    else:
        form = RestaurantUpdateForm(instance=restaurant)

    context = {
        'restaurant': restaurant,
        'form': form,
    }

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/edit_restaurant.html',
        context
    )


def add_menu_item(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user
    )

    if request.method == 'POST':
        form = MenuItemForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            menu_item = form.save(commit=False)

            # Automatically associate the item with this restaurant.
            menu_item.restaurant = restaurant

            menu_item.save()

            messages.success(
                request,
                f'{menu_item.name} was added to your menu successfully.'
            )

            return redirect(
                'restaurant_applicants:manage_restaurant',
                restaurant_id=restaurant.id
            )

    else:
        form = MenuItemForm()

    context = {
        'restaurant': restaurant,
        'form': form,
    }

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/add_menu_item.html',
        context
    )


def edit_menu_item(request, restaurant_id, item_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user,
        status='approved'
    )

    menu_item = get_object_or_404(
        MenuItem,
        id=item_id,
        restaurant=restaurant
    )

    if request.method == 'POST':

        form = MenuItemForm(
            request.POST,
            request.FILES,
            instance=menu_item
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'"{menu_item.name}" was successfully updated.'
            )

            return redirect(
                'restaurant_applicants:manage_restaurant',
                restaurant_id=restaurant.id
            )

    else:

        form = MenuItemForm(instance=menu_item)

    return render(
        request,
        'Restaurant_Applicants/my-restaurant/add_menu_item.html',
        {
            'restaurant': restaurant,
            'form': form,
            'menu_item': menu_item,
            'is_edit': True,
        }
    )


@require_POST
def delete_menu_item(request, restaurant_id, item_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
        owner=request.user,
        status='approved'
    )

    menu_item = get_object_or_404(
        MenuItem,
        id=item_id,
        restaurant=restaurant
    )

    item_name = menu_item.name

    menu_item.delete()

    messages.success(
        request,
        f'"{item_name}" was successfully deleted.'
    )

    return redirect(
        'restaurant_applicants:manage_restaurant',
        restaurant_id=restaurant.id
    )