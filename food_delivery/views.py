
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Restaurant, RestaurantOperatingHour
from .forms import (
    RestaurantRegistrationForm,
    RestaurantProfileForm,
    OperatingHourFormSet,
)


def base_view(request):
    return render(request, 'food_delivery/restaurant/base.html')

from datetime import time

@login_required
def restaurant_register(request):

    if request.method == 'POST':
        form = RestaurantRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            try:
                with transaction.atomic():

                    restaurant = form.save(commit=False)
                    restaurant.owner = request.user
                    restaurant.status = 'pending'
                    restaurant.save()

                    # Default operating hours
                    default_hours = {
                        'monday': (time(8, 0), time(22, 0)),
                        'tuesday': (time(8, 0), time(22, 0)),
                        'wednesday': (time(8, 0), time(22, 0)),
                        'thursday': (time(8, 0), time(22, 0)),
                        'friday': (time(8, 0), time(23, 0)),
                        'saturday': (time(9, 0), time(23, 0)),
                        'sunday': (time(10, 0), time(21, 0)),
                    }

                    hours = []

                    for day, times in default_hours.items():
                        hours.append(
                            RestaurantOperatingHour(
                                restaurant=restaurant,
                                day=day,
                                opening_time=times[0],
                                closing_time=times[1],
                                is_closed=False
                            )
                        )

                    RestaurantOperatingHour.objects.bulk_create(hours)

                messages.success(
                    request,
                    'Your restaurant has been registered successfully. '
                    'It is now awaiting administrator approval.'
                )

                return redirect(
                    'restaurant_profile',
                    pk=restaurant.pk
                )

            except Exception as e:
                messages.error(
                    request,
                    f'An error occurred while saving your restaurant: {e}'
                )

        else:
            # Display validation errors
            print("RESTAURANT FORM ERRORS:", form.errors)
            print("NON-FIELD ERRORS:", form.non_field_errors())

            messages.error(
                request,
                'Please correct the errors in the registration form.'
            )

    else:
        form = RestaurantRegistrationForm(
            initial={'country': 'Kenya'}
        )

    return render(
        request,
        'food_delivery/restaurants/restaurant_register.html',
        {'form': form}
    )


def restaurant_profile(request, pk):

    restaurant = get_object_or_404(
        Restaurant,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        form = RestaurantProfileForm(
            request.POST,
            request.FILES,
            instance=restaurant
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Restaurant information updated successfully.'
            )

            return redirect(
                'restaurant_profile',
                pk=restaurant.pk
            )

    else:
        form = RestaurantProfileForm(instance=restaurant)

    return render(
        request,
        'food_delivery/restaurants/restaurant_profile.html',
        {
            'restaurant': restaurant,
            'form': form,
        }
    )



def restaurant_operating_hours(request, pk):

    restaurant = get_object_or_404(
        Restaurant,
        pk=pk,
        owner=request.user
    )

    formset = OperatingHourFormSet(
        request.POST or None,
        instance=restaurant
    )

    if request.method == 'POST' and formset.is_valid():

        valid_hours = True

        for form in formset.forms:
            data = form.cleaned_data

            if not data or data.get('DELETE'):
                continue

            if not data.get('is_closed'):
                if not data.get('opening_time') or not data.get('closing_time'):
                    form.add_error(
                        'opening_time',
                        'Opening and closing times are required for an open day.'
                    )
                    valid_hours = False

        if valid_hours:
            formset.save()

            messages.success(
                request,
                'Restaurant operating hours updated successfully.'
            )

            return redirect(
                'restaurant_operating_hours',
                pk=restaurant.pk
            )

    return render(
        request,
        'food_delivery/restaurants/restaurant_hours.html',
        {
            'restaurant': restaurant,
            'formset': formset,
        }
    )
