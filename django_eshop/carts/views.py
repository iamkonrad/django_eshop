from django.contrib.auth.decorators import login_required
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
    current_user= request.user
    product = Product.objects.get(id=product_id)                                                                        #fetching the product; PRODUCT

    #FOR AN AUTHENTICATED USER
    if current_user.is_authenticated:
        product_variation = []                                                                                          #assigning the variations to a list
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                                                                                        #checking whether an item (with key value pair) exists within a database
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)                                     #existing variations
            ex_var_list = []                                                                                            #existing variations list
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1                                                                                      #increasing the quantity if variation is already
                item.save()                                                                                             #inside the cart

            else:                                                                                                       #if variation not inside the cart creating a new cart item
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:                                                                          #product variations for the cart item
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    item.save()
        else:                                                                                                           #creating a new cart item if there is none(quantity=1); linked
            cart_item = CartItem.objects.create(                                                                        #to current product and cart
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

#FOR AN UNAUTHENTICATED USER
    else:
        product_variation=[]                                                                                            #assigning the variations to a list
        if request.method =="POST":
            for item in request.POST:
                key=item
                value=request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,                  #checking whether an item (with key value pair) exists within a database
                                                      variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))                                                            #retrieving the cart based on the present session id
        except Cart.DoesNotExist:                                                                                       #if no cart exists a new one is created using the present session id
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)                                             #existing variations
            ex_var_list=[]                                                                                              #existing variations list
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id= id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity +=1                                                                                       #increasing the quaantity if variation is already
                item.save()                                                                                             #inside the cart

            else:                                                                                                       #if variation not inside the cart creating a new cart item
                item = CartItem.objects.create(product=product,quantity=1, cart=cart)
                if len(product_variation)>0:                                                                            #product variations for the cart item
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    item.save()
        else:                                                                                                           #creating a new cart item if there is none(quantity=1); linked
            cart_item = CartItem.objects.create(                                                                        #to current product and cart
                product=product,
                quantity = 1,
                cart=cart,
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')                                                                                         #redirection, updated cart

def remove_cart(request, product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product_id, user=request.user,
                                             id=cart_item_id)                                                           # cart item matching product's and cart's ID
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))                                                          # the cart id from the request
            cart_item = CartItem.objects.get(product=product_id, cart=cart,                                             #cart item matching product's and cart's ID
                                             id=cart_item_id)  # cart item matching product's and cart's ID

        if cart_item.quantity > 1:                                                                                      #if the quantity > 1 it gets decreased by 1
            cart_item.quantity -=1                                                                                      #if it's 1 then the cart item is deleted
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request,product_id, cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))                                                              #retrieving cart id from the current session
        cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
    cart_item.delete()                                                                                                  #remove cart item irrespective of its quantity
    return redirect('cart')

def cart(request, total=0, quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))                                                            #retrieving user's cart object based on cart id within the current session
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)                                                #retrieving all active items associated with the fetched cart
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)                                                      #subtotal, product price by its quantity, adding to the total
            quantity += cart_item.quantity                                                                              #adding the quantity of every cart item to the overall one
        tax = round((16 * total) / 100, 2)
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

@login_required(login_url='login')
def checkout(request, total=0, quantity=0,cart_items=None):
    tax=0
    grand_total=0
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart = Cart.objects.get(
            cart_id=_cart_id(request))  # retrieving user's cart object based on cart id within the current session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))                                                                #retrieving user's cart object based on cart id within the current session
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)                                                    #retrieving all active items associated with the fetched cart
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)                                                      #subtotal, product price by its quantity, adding to the total
            quantity += cart_item.quantity                                                                              #adding the quantity of every cart item to the overall one
        tax = round((16 * total) / 100, 2)
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

    return render(request,'store/checkout.html', context)

