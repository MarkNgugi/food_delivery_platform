
from django import forms
from django.forms import inlineformset_factory

from .models import Restaurant, RestaurantOperatingHour


class RestaurantRegistrationForm(forms.ModelForm):

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
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': "e.g. Mama Njeri's Kitchen"
            }),

            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell customers about your restaurant...'
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g. 0712345678'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'restaurant@example.com'
            }),

            'country': forms.TextInput(attrs={
                'readonly': 'readonly'
            }),

            'county': forms.TextInput(attrs={
                'placeholder': 'e.g. Kiambu'
            }),

            'town': forms.TextInput(attrs={
                'placeholder': 'e.g. Ruiru'
            }),

            'area': forms.TextInput(attrs={
                'placeholder': 'e.g. Kimbo'
            }),

            'street': forms.TextInput(attrs={
                'placeholder': 'e.g. Thika Road'
            }),

            'building': forms.TextInput(attrs={
                'placeholder': 'Building name or number'
            }),

            'landmark': forms.TextInput(attrs={
                'placeholder': 'Nearby landmark'
            }),

            'additional_directions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional directions for delivery riders...'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                'Enter a valid phone number using digits only.'
            )

        if len(phone) not in (9, 10, 12):
            raise forms.ValidationError(
                'Enter a valid Kenyan phone number.'
            )

        return phone


class RestaurantProfileForm(forms.ModelForm):

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
        ]


OperatingHourFormSet = inlineformset_factory(
    Restaurant,
    RestaurantOperatingHour,
    fields=[
        'day',
        'opening_time',
        'closing_time',
        'is_closed',
    ],
    extra=0,
    can_delete=False,
    widgets={
        'day': forms.Select(),
        'opening_time': forms.TimeInput(attrs={
            'type': 'time'
        }),
        'closing_time': forms.TimeInput(attrs={
            'type': 'time'
        }),
        'is_closed': forms.CheckboxInput(),
    }
)
