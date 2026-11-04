
from django import forms
from django.forms import inlineformset_factory

from .models import Restaurant, RestaurantOperatingHour
from .models import MenuItem, MenuCategory




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


class RestaurantUpdateForm(forms.ModelForm):

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
                'placeholder': 'e.g. Savora Bistro',
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Tell customers about your restaurant...',
                'rows': 4,
            }),

            'cuisine': forms.Select(),

            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g. 0712345678',
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'restaurant@example.com',
            }),

            'country': forms.TextInput(),

            'county': forms.TextInput(attrs={
                'placeholder': 'e.g. Kiambu',
            }),

            'town': forms.TextInput(attrs={
                'placeholder': 'e.g. Ruiru',
            }),

            'area': forms.TextInput(attrs={
                'placeholder': 'e.g. Kimbo',
            }),

            'street': forms.TextInput(attrs={
                'placeholder': 'Street name',
            }),

            'building': forms.TextInput(attrs={
                'placeholder': 'Building name or number',
            }),

            'landmark': forms.TextInput(attrs={
                'placeholder': 'Nearby landmark',
            }),

            'additional_directions': forms.Textarea(attrs={
                'placeholder': 'Provide any extra directions that will help customers find you...',
                'rows': 4,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
            })

        self.fields['logo'].required = False
        self.fields['cover_image'].required = False



class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem

        fields = [
            'name',
            'category',
            'description',
            'image',
            'price',
            'discount_price',
            'preparation_time',
            'serving_size',
            'ingredients',
            'allergens',
            'is_available',
            'is_active',
            'is_featured',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Grilled Chicken'
            }),

            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe this meal...'
            }),

            'category': forms.Select(),

            'price': forms.NumberInput(attrs={
                'placeholder': 'e.g. 850.00',
                'step': '0.01',
                'min': '0'
            }),

            'discount_price': forms.NumberInput(attrs={
                'placeholder': 'Optional discounted price',
                'step': '0.01',
                'min': '0'
            }),

            'preparation_time': forms.NumberInput(attrs={
                'placeholder': 'e.g. 20',
                'min': '1'
            }),

            'serving_size': forms.TextInput(attrs={
                'placeholder': 'e.g. Serves 1'
            }),

            'ingredients': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'List the main ingredients...'
            }),

            'allergens': forms.TextInput(attrs={
                'placeholder': 'e.g. Milk, eggs, peanuts'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = MenuCategory.objects.filter(
            is_active=True
        )

    def clean(self):
        cleaned_data = super().clean()

        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')

        if price is not None and price <= 0:
            self.add_error('price', 'Price must be greater than zero.')

        if discount_price is not None:
            if discount_price <= 0:
                self.add_error(
                    'discount_price',
                    'Discount price must be greater than zero.'
                )
            elif price is not None and discount_price >= price:
                self.add_error(
                    'discount_price',
                    'Discount price must be lower than the normal price.'
                )

        return cleaned_data