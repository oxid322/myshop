from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int)
    #указывает должно ли кол-во быть прибалено к
    #к любому существующему кол-ву в корзине или должно быть переопределение
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)
