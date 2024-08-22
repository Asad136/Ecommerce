from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

from .models import User

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'address']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number','address','role', 'password1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('buyer', 'Buyer'), ('seller', 'Seller')]

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    class Meta:
        model = User
        fields = ('email', 'password')