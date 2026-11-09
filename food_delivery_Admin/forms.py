
from django import forms
from django.forms import inlineformset_factory

from food_delivery.models import (
    Restaurant,
    RestaurantOperatingHour,
)


class AdminRestaurantUpdateForm(forms.ModelForm):

    class Meta:
        model = Restaurant

        fields = [
            'name',
            'description',
            'cuisine',
            'logo',
            'cover_image',
            'phone',
            'email',
            'country',
            'county',
            'town',
            'area',
            'street',
            'building',
            'landmark',
            'additional_directions',
            'status',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Restaurant name',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the restaurant',
            }),

            'cuisine': forms.Select(attrs={
                'class': 'form-control',
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254...',
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'restaurant@example.com',
            }),

            'country': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'county': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'town': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'area': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'street': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'building': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'landmark': forms.TextInput(attrs={
                'class': 'form-control',
            }),

            'additional_directions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),

            'status': forms.Select(attrs={
                'class': 'form-control',
            }),

            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),

            'cover_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


class RestaurantOperatingHourForm(forms.ModelForm):

    class Meta:
        model = RestaurantOperatingHour

        fields = [
            'day',
            'opening_time',
            'closing_time',
            'is_closed',
        ]

        widgets = {
            'day': forms.Select(attrs={
                'class': 'form-control',
            }),

            'opening_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),

            'closing_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),

            'is_closed': forms.CheckboxInput(attrs={
                'class': 'closed-checkbox',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        is_closed = cleaned_data.get('is_closed')

        if is_closed:
            cleaned_data['opening_time'] = None
            cleaned_data['closing_time'] = None

        return cleaned_data


RestaurantOperatingHourFormSet = inlineformset_factory(
    Restaurant,
    RestaurantOperatingHour,
    form=RestaurantOperatingHourForm,
    extra=0,
    can_delete=False,
)


from django import forms
from food_delivery.models import Cuisine


class CuisineForm(forms.ModelForm):

    class Meta:
        model = Cuisine
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Kenyan Cuisine',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Briefly describe this cuisine category...',
                'rows': 4,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        # Case-insensitive duplicate protection.
        existing = Cuisine.objects.filter(
            name__iexact=name
        )

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError(
                'A cuisine category with this name already exists.'
            )

        return name