from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import CartItem
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.contrib import messages


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
    if 'keyword' in request.GET:                                                                                        # extracting the search keyword value
        keyword = request.GET['keyword']                                                                                #storing it inside the keyword variable
        if keyword:
            products = Product.objects.order_by('created_date').filter(Q(description__icontains=keyword)|                #looking for a product reference in description and product_name
                                                                       Q(product_name__icontains=keyword))               #by keyword
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request,'store/store.html',context)

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
