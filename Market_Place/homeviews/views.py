from django.shortcuts import render
from store.models import Product

def home(request):
    products= Product.objects.all()
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'landing.html', {'products': products})

