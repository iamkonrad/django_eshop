from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category


def store(request, category_slug=None):                                                                                 #default set to None
    categories=None                                                                                                     #default set to None
    products=None                                                                                                       #default set to None

    if category_slug != None:                                                                                           #fetch products associated with a category
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)                                                      #fetch all available products without filtering by category
        product_count = products.count()                                                                                #counting the products and assigning the number to a variabe

    context = {
        'products':products,
        'product_count':product_count,
    }
    return render (request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product= Product.objects.get(category__slug=category_slug, slug=product_slug)                            #accessing Product model's category and Category model's
                                                                                                                        #slug; retrieving a product equal to given category slug and
    except Exception as e:                                                                                              #product slug
        raise e

    context={
        'single_product':single_product,
    }
    return render(request, 'store/product_detail.html', context)