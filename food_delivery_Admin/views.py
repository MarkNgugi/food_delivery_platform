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



from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from food_delivery.models import (
    Restaurant,
    RestaurantOperatingHour,
    Cuisine,
)

from .forms import (
    AdminRestaurantUpdateForm,
    RestaurantOperatingHourFormSet,
)


# ==========================================================
# RESTAURANT LIST
# ==========================================================

@staff_member_required
def restaurants(request):

    restaurant_list = Restaurant.objects.select_related(
        'owner',
        'cuisine'
    ).order_by('-created_at')

    # ------------------------------------------------------
    # SUMMARY STATISTICS
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # STATUS FILTER
    # ------------------------------------------------------

    selected_status = request.GET.get(
        'status', ''
    ).strip()

    valid_statuses = [
        'approved',
        'pending',
        'suspended',
        'rejected',
    ]

    if selected_status in valid_statuses:

        restaurant_list = restaurant_list.filter(
            status=selected_status
        )

    elif selected_status:

        selected_status = ''

    # ------------------------------------------------------
    # COUNTY FILTER
    # ------------------------------------------------------

    selected_county = request.GET.get(
        'county', ''
    ).strip()

    if selected_county:

        restaurant_list = restaurant_list.filter(
            county__iexact=selected_county
        )

    # ------------------------------------------------------
    # CUISINE FILTER
    # ------------------------------------------------------

    selected_cuisine = request.GET.get(
        'cuisine', ''
    ).strip()

    if selected_cuisine.isdigit():

        restaurant_list = restaurant_list.filter(
            cuisine_id=int(selected_cuisine)
        )

    else:
        selected_cuisine = ''

    # ------------------------------------------------------
    # COUNTY OPTIONS
    # ------------------------------------------------------

    counties = (
        Restaurant.objects
        .exclude(county__isnull=True)
        .exclude(county__exact='')
        .values_list('county', flat=True)
        .distinct()
        .order_by('county')
    )

    # ------------------------------------------------------
    # CUISINE OPTIONS
    # ------------------------------------------------------

    cuisines = Cuisine.objects.all().order_by('name')

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

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


# ==========================================================
# RESTAURANT DETAILS
# ==========================================================

@staff_member_required
def restaurant_detail(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant.objects.select_related(
            'owner',
            'cuisine'
        ),
        id=restaurant_id
    )

    operating_hours = restaurant.operating_hours.all()

    context = {
        'restaurant': restaurant,
        'operating_hours': operating_hours,
    }

    return render(
        request,
        'food_delivery_Admin/restaurants/restaurant_detail.html',
        context
    )


# ==========================================================
# RESTAURANT EDIT
# ==========================================================

@staff_member_required
def restaurant_edit(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant.objects.select_related(
            'owner',
            'cuisine'
        ),
        id=restaurant_id
    )

    # Ensure all seven operating days exist.
    # This also supports older restaurants that may have
    # incomplete operating-hour records.

    with transaction.atomic():

        for day, label in RestaurantOperatingHour.DAYS_OF_WEEK:

            RestaurantOperatingHour.objects.get_or_create(
                restaurant=restaurant,
                day=day,
            )

    if request.method == 'POST':

        form = AdminRestaurantUpdateForm(
            request.POST,
            request.FILES,
            instance=restaurant,
        )

        operating_hours_formset = RestaurantOperatingHourFormSet(
            request.POST,
            instance=restaurant,
        )

        if (
            form.is_valid()
            and operating_hours_formset.is_valid()
        ):

            with transaction.atomic():

                form.save()

                operating_hours_formset.save()

            messages.success(
                request,
                f'{restaurant.name} was updated successfully.'
            )

            return redirect(
                'food_delivery_Admin:restaurant_detail',
                restaurant_id=restaurant.id,
            )

        messages.error(
            request,
            'Please correct the errors in the form.'
        )

    else:

        form = AdminRestaurantUpdateForm(
            instance=restaurant,
        )

        operating_hours_formset = RestaurantOperatingHourFormSet(
            instance=restaurant,
        )

    context = {
        'restaurant': restaurant,
        'form': form,
        'operating_hours_formset': operating_hours_formset,
    }

    return render(
        request,
        'food_delivery_Admin/restaurants/restaurant_edit.html',
        context
    )


# ==========================================================
# RESTAURANT DELETE
# ==========================================================

@staff_member_required
def restaurant_delete(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id,
    )

    if request.method == 'POST':

        restaurant_name = restaurant.name

        try:

            with transaction.atomic():

                restaurant.delete()

            messages.success(
                request,
                f'{restaurant_name} was permanently deleted.'
            )

            return redirect(
                'food_delivery_Admin:restaurants'
            )

        except ProtectedError:

            messages.error(
                request,
                'This restaurant cannot be deleted because '
                'other records depend on it. Suspend it instead.'
            )

            return redirect(
                'food_delivery_Admin:restaurant_detail',
                restaurant_id=restaurant.id,
            )

    return render(
        request,
        'food_delivery_Admin/restaurants/restaurant_delete.html',
        {
            'restaurant': restaurant,
        }
    )




def orders(request):
    return render(request,'food_delivery_Admin/orders/orders.html')

def menu_management(request):
    return render(request,'food_delivery_Admin/menu_management/menu_management.html')

def customers(request):
    return render(request,'food_delivery_Admin/customers/customers.html')

def delivery_management(request):
    return render(request,'food_delivery_Admin/delivery_management/delivery_management.html')


def restaurant_owners(request):
    return render(request,'food_delivery_Admin/restaurant_owners/restaurant_owners.html')


def cuisine_categories(request):
    return render(request,'food_delivery_Admin/cuisine_categories/cuisine_categories.html')


def reports_analytics(request):
    return render(
        request,
        'food_delivery_Admin/reports_analytics/reports_analytics.html'
    )


def admin_settings(request):
    return render(
        request,
        'food_delivery_Admin/settings/settings.html'
    )

