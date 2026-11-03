from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cuisines'

    def __str__(self):
        return self.name


class Restaurant(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='restaurants'
    )

    # Restaurant information
    name = models.CharField(max_length=200)
    description = models.TextField()
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='restaurants'
    )

    logo = models.ImageField(
        upload_to='restaurants/logos/',
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to='restaurants/covers/',
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Restaurant location
    country = models.CharField(max_length=100, default='Kenya')
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    area = models.CharField(
        max_length=150,
        help_text='Estate or neighbourhood, e.g. Kimbo'
    )
    street = models.CharField(max_length=150, blank=True)
    building = models.CharField(max_length=150, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    additional_directions = models.TextField(blank=True)

    # Registration status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        parts = [
            self.building,
            self.street,
            self.area,
            self.town,
            self.county,
            self.country,
        ]
        return ', '.join(part for part in parts if part)


class RestaurantOperatingHour(models.Model):

    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='operating_hours'
    )

    day = models.CharField(
        max_length=15,
        choices=DAYS_OF_WEEK
    )

    opening_time = models.TimeField(
        null=True,
        blank=True
    )

    closing_time = models.TimeField(
        null=True,
        blank=True
    )

    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'day'],
                name='unique_restaurant_operating_day'
            )
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.get_day_display()}'
