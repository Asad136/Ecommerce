from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('buyer', 'Buyer'), ('seller', 'Seller')]
        self.fields.pop('password2')  

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    class Meta:
        model = User
        fields = ('email', 'password')