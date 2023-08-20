from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import CartItem
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import  Paginator
from django.contrib import messages



def store(request, category_slug=None):

    if category_slug:                                                                                                   #products queryset
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)

    min_price = request.GET.get('min_price')                                                                            #filter by price range
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 9)                                                                                  #pagination
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products':paged_products,
        'product_count':product_count,

    }
    return render (request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:                                                                                                                #accessing Product model's category and Category model's slug;
        single_product= Product.objects.get(category__slug=category_slug, slug=product_slug)                            #retrieving a product equal to given category slug and product slug;
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()             #filtering products, returning True or False, based on whether they exist in a cart;
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id,status=True)                                     #Get the reviews

    product_gallery=ProductGallery.objects.filter(product_id=single_product.id)

    context={
        'single_product':single_product,
        'in_cart': in_cart,
        'orderproduct':orderproduct,
        'reviews': reviews,
        'product_gallery':product_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    keyword = request.GET.get('keyword')

    if keyword:                                                                                                         #first try to search it by keyword
        products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))

        if not products:                                                                                                #if keyword doesn't match then follow the logic
            if keyword.endswith('s'):
                products = Product.objects.filter(
                    Q(description__icontains=keyword[:-1]) | Q(product_name__icontains=keyword[:-1]))
            elif keyword.endswith('es'):
                products = Product.objects.filter(
                    Q(description__icontains=keyword[:-2]) | Q(product_name__icontains=keyword[:-2]))
            elif keyword.endswith('ies'):
                singular_keyword = keyword[:-3] + 'y'
                products = Product.objects.filter(
                    Q(description__icontains=singular_keyword) | Q(product_name__icontains=singular_keyword))
            else:
                products = Product.objects.filter(
                    Q(description__icontains=keyword + 's') | Q(product_name__icontains=keyword + 's'))

        product_count = products.count()

        context = {
            'products': products,
            'product_count': product_count,
        }
        return render(request, 'store/store.html', context)

    return render(request, 'store/store.html')

def submit_review(request, product_id):
    url=request.META.get('HTTP_REFERER')
    if request.method=='POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,'Thank. Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request, 'Thank. Your review has been submitted.')
                return redirect(url)
