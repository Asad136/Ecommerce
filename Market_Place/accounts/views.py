from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,EmailAuthenticationForm,CustomUserChangeForm
from django.contrib import messages
from store.models import Product,Store
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .models import User
from .models import User

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            # token is generated here
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # activation link build 
            activation_link = request.build_absolute_uri(
                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
            )
            # Send activation email
            subject = 'Activate Your Account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Please check your email to activate your account.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})



def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('signup')


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
                        return redirect('seller_landing_page')
                else:
                    return redirect('admin_landing')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def view_profile(request):
    return render(request, 'accounts/view_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
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

@login_required
def admin_landing(request):
    products= Product.objects.all()
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    return render(request,'admin_landing.html',{'products': products})


def seller_landing_page(request):

    return render(request,'seller_landing_page.html')