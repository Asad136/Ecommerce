from django import forms
from .models import Store,Product

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('store_pic', 'name', 'description')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_pic', 'name', 'description', 'price', 'stock']
