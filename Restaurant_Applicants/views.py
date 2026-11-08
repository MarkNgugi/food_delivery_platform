from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.http import require_POST
from datetime import date

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





from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def orders(request):

    # DEMO DATA ONLY
    # These are sample orders for displaying the Orders page.
    # They are not yet connected to the database.

    all_orders = [
        {
            'order_number': 'SAV-00125',
            'customer_name': 'John Mwangi',
            'customer_phone': '0712 345 678',
            'created_at': datetime(2026, 11, 8, 14, 30),
            'items_count': 3,
            'total': 1850,
            'status': 'pending',
        },
        {
            'order_number': 'SAV-00124',
            'customer_name': 'Mary Wanjiku',
            'customer_phone': '0722 456 789',
            'created_at': datetime(2026, 11, 8, 13, 15),
            'items_count': 2,
            'total': 1200,
            'status': 'accepted',
        },
        {
            'order_number': 'SAV-00123',
            'customer_name': 'Peter Kamau',
            'customer_phone': '0701 234 567',
            'created_at': datetime(2026, 11, 7, 18, 45),
            'items_count': 4,
            'total': 2450,
            'status': 'preparing',
        },
        {
            'order_number': 'SAV-00122',
            'customer_name': 'Jane Achieng',
            'customer_phone': '0715 222 333',
            'created_at': datetime(2026, 11, 7, 12, 20),
            'items_count': 1,
            'total': 750,
            'status': 'completed',
        },
        {
            'order_number': 'SAV-00121',
            'customer_name': 'David Otieno',
            'customer_phone': '0720 111 222',
            'created_at': datetime(2026, 11, 6, 19, 10),
            'items_count': 2,
            'total': 1600,
            'status': 'rejected',
        },
        {
            'order_number': 'SAV-00120',
            'customer_name': 'Grace Njeri',
            'customer_phone': '0790 555 666',
            'created_at': datetime(2026, 11, 6, 11, 45),
            'items_count': 3,
            'total': 2100,
            'status': 'completed',
        },
    ]

    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    search_query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()

    filtered_orders = all_orders

    # Search by order number, customer name or phone number.
    if search_query:
        filtered_orders = [
            order for order in filtered_orders
            if search_query.lower() in order['order_number'].lower()
            or search_query.lower() in order['customer_name'].lower()
            or search_query.lower() in order['customer_phone'].lower()
        ]

    # Filter orders by status.
    valid_statuses = [value for value, label in status_choices]

    if selected_status in valid_statuses:
        filtered_orders = [
            order for order in filtered_orders
            if order['status'] == selected_status
        ]
    else:
        selected_status = ''

    context = {
        'orders': filtered_orders,
        'search_query': search_query,
        'selected_status': selected_status,
        'status_choices': status_choices,
        'today': date.today(),

        # Order statistics
        'total_orders': len(all_orders),

        'pending_orders': sum(
            1 for order in all_orders
            if order['status'] == 'pending'
        ),

        'preparing_orders': sum(
            1 for order in all_orders
            if order['status'] == 'preparing'
        ),

        'completed_orders': sum(
            1 for order in all_orders
            if order['status'] == 'completed'
        ),
    }

    return render(
        request,
        'Restaurant_Applicants/orders/orders.html',
        context
    )
