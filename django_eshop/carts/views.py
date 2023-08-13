from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from carts.models import Cart, CartItem
from store.models import Product


def _cart_id(request):                                                                                                  #private function
    cart = request.session.session_key                                                                                  #session id
    if not cart:
        cart = request.session.create()                                                                                 #if there is no session_key a new one is created
    return cart

def add_cart (request, product_id):
    product = Product.objects.get(id=product_id)                                                                        #fetching the product
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


def cart(request, total=0, quantity=0,cart_items=None):
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
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
