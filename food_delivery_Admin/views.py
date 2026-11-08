from django.shortcuts import render
from . import views

def dashboard(request):
    return render(request,'food_delivery_Admin/dashboard.html')


from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from food_delivery.models import Restaurant


def restaurants(request):

    # Get restaurants with related owner and cuisine information.
    restaurant_list = Restaurant.objects.select_related(
        'owner',
        'cuisine'
    ).order_by('-created_at')

    # Summary statistics.
    total_restaurants = Restaurant.objects.count()

    approved_restaurants = Restaurant.objects.filter(
        status='approved'
    ).count()

    pending_restaurants = Restaurant.objects.filter(
        status='pending'
    ).count()

    suspended_restaurants = Restaurant.objects.filter(
        status='suspended'
    ).count()

    # Search
    search_query = request.GET.get('q', '').strip()

    if search_query:
        restaurant_list = restaurant_list.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(owner__first_name__icontains=search_query) |
            Q(owner__last_name__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(town__icontains=search_query) |
            Q(county__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(cuisine__name__icontains=search_query)
        )

    # Status filter
    selected_status = request.GET.get('status', '').strip()

    valid_statuses = [
        'approved',
        'pending',
        'suspended',
        'rejected'
    ]

    if selected_status in valid_statuses:
        restaurant_list = restaurant_list.filter(
            status=selected_status
        )

    # County filter
    selected_county = request.GET.get('county', '').strip()

    if selected_county:
        restaurant_list = restaurant_list.filter(
            county__iexact=selected_county
        )

    # Cuisine filter
    selected_cuisine = request.GET.get('cuisine', '').strip()

    if selected_cuisine.isdigit():
        restaurant_list = restaurant_list.filter(
            cuisine_id=int(selected_cuisine)
        )

    # County dropdown options
    counties = (
        Restaurant.objects
        .exclude(county__exact='')
        .values_list('county', flat=True)
        .distinct()
        .order_by('county')
    )

    # Cuisine dropdown options
    cuisines = (
        Restaurant.objects
        .filter(cuisine__isnull=False)
        .values('cuisine_id', 'cuisine__name')
        .distinct()
        .order_by('cuisine__name')
    )

    # Pagination
    paginator = Paginator(restaurant_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'restaurants': page_obj,
        'page_obj': page_obj,

        'total_restaurants': total_restaurants,
        'approved_restaurants': approved_restaurants,
        'pending_restaurants': pending_restaurants,
        'suspended_restaurants': suspended_restaurants,

        'search_query': search_query,
        'selected_status': selected_status,
        'selected_county': selected_county,
        'selected_cuisine': selected_cuisine,

        'counties': counties,
        'cuisines': cuisines,
    }

    return render(
        request,
        'food_delivery_Admin/restaurants/restaurants.html',
        context
    )
