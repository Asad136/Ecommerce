from django.shortcuts import render

def home(request):
    return render(request, 'landing.html')
def detail_page(request):
    return render(request, 'details.html')
