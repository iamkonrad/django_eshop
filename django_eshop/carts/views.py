from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import Cart, CartItem
from store.models import Product, Variation


def _cart_id(request):                                                                                                  #private function
    cart = request.session.session_key                                                                                  #session id
    if not cart:
        cart = request.session.create()                                                                                 #if there is no session_key a new one is created
    return cart

def add_cart (request, product_id):
    product = Product.objects.get(id=product_id)                                                                        #fetching the product
    product_variation=[]
    if request.method =="POST":
        for item in request.POST:
            key=item
            value=request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,                      #checking whether an item (with key value pair) exists within a database
                                                  variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass


    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))                                                                #retrieving the cart based on the present session id
    except Cart.DoesNotExist:                                                                                           # if no cart exists a new one is created using the present session id
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:                                                                                                                #finding existing cart item for the specific product and cart
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.quantity +=1                                                                                          #if the item exists in the cart, quantity incremented by one
        cart_item.save()
    except CartItem.DoesNotExist:                                                                                       #creating a new cart item if there is none(quantity=1); linked
        cart_item = CartItem.objects.create(                                                                            #to current product and cart
            product=product,
            quantity = 1,
            cart=cart,
        )
        cart_item.save()
    return redirect('cart')                                                                                             #redirection, updated cart


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))                                                                  #the cart id from the request
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product_id, cart=cart)                                                     #cart item matching product's and cart's ID
    if cart_item.quantity > 1:                                                                                          #if the qunatity > 1 it gets decreased by 1
        cart_item.quantity -=1                                                                                          #if it's 1 then the cart item is deleted
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))                                                                  #retrieving cart id from the urrent session
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()                                                                                                  #remove cart item irrespective of its quantity
    return redirect('cart')

def cart(request, total=0, quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))                                                                #retrieving user's cart object based on cart id within the current session
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)                                                    #retrieving all active items associated with the fetched cart
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)                                                      #subtotal, product price by its quantity, adding to the total
            quantity += cart_item.quantity                                                                              #adding the quantity of every cart item to the overall one
            tax = (16 * total)/100
            grand_total = total +tax

    except ObjectDoesNotExist:
        pass                                                                                                            #in case no cart exists throw an exception
    context = {
        'total': "{:.2f}".format(total),
        'quantity':quantity,
        'cart_items':cart_items,
        'tax': "{:.2f}".format(tax),
        'grand_total': "{:.2f}".format(grand_total),
    }
    return render(request, 'store/cart.html', context)
