from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from store.models import Product
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator


def store(request, category_slug=None):                                                                                 #default set to None
    categories=None                                                                                                     #default set to None
    products=None                                                                                                       #default set to None

    if category_slug != None:                                                                                           #fetch products associated with a category
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 9)                                                                              # number of products displayed per page
        page = request.GET.get('page')                                                                                  # passing page number through get method
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:                                                                                                               #fetch all available products without filtering by category
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 9)                                                                              # number of products displayed per page
        page = request.GET.get('page')                                                                                  # passing page number through get method
        paged_products = paginator.get_page(page)
        product_count = products.count()                                                                                #counting the products and assigning the number to a variabe

    context = {
        'products':paged_products,                                                                                      # paged 9 products
        'product_count':product_count,

    }
    return render (request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:                                                                                                                #accessing Product model's category and Category model's slug;
        single_product= Product.objects.get(category__slug=category_slug, slug=product_slug)                            #retrieving a product equal to given category slug and product slug;
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()             #filtering products, returning True or False, based on whether they exist in a cart;
    except Exception as e:
        raise e

    context={
        'single_product':single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)