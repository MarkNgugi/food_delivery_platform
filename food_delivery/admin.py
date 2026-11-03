from django.contrib import admin
from .models import Cuisine, Restaurant, RestaurantOperatingHour


class RestaurantOperatingHourInline(admin.TabularInline):
    model = RestaurantOperatingHour
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'town',
        'county',
        'status',
        'created_at',
    )

    list_filter = ('status', 'county', 'cuisine')
    search_fields = ('name', 'owner__username', 'town', 'phone')
    inlines = [RestaurantOperatingHourInline]


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(RestaurantOperatingHour)
class RestaurantOperatingHourAdmin(admin.ModelAdmin):
    list_display = (
        'restaurant',
        'day',
        'opening_time',
        'closing_time',
        'is_closed',
    )
    list_filter = ('day', 'is_closed')