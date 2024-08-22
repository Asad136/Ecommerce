from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.all()
    return render(request, 'landing.html', {'products': products})
def detail_page(request):
    return render(request, 'details.html')
