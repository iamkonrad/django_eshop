from django.shortcuts import render
from store.models import Product


def store(request):
    products = Product.objects.all().filter(is_available=True)                                                          #filtering by the availability of a product
    product_count = products.count()                                                                                    #counting the products and assigning the nubmer to a variabe

    context = {
        'products':products,
        'product_count':product_count,
    }
    return render (request, 'store/store.html', context)
