from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate,logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,EmailAuthenticationForm
from django.contrib import messages
from store.models import Product

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'buyer':
                    return redirect('buyer_landing')
                elif user.role == 'seller':
                    if hasattr(user, 'store'):
                        return redirect('store_detail', pk=user.store.pk)
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return render(request,'landing.html')

@login_required
def buyer_landing(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'buyer_landing.html', {'products': products})