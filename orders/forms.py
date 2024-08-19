from django import forms
from .models import Order
from localflavor.ru.forms import RUPostalCodeField
from localflavor.us.forms import USZipCodeField

class RUOrderCreateForm(forms.ModelForm):

    postal_code = RUPostalCodeField()
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

class USOrderCreateForm(forms.ModelForm):

    postal_code = USZipCodeField()
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']