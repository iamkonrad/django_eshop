from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True)                                                          #filtering by the availability of a products

    context = {
        'products':products,
    }

    return render (request, 'home.html',context)