from django.shortcuts import render
from .models import Product

def main(request):
    return render(request, 'main/main.html')
    
def catalog(request):
    products = Product.objects.all()
    return render(request, 'main/catalog.html', {'products': products})
