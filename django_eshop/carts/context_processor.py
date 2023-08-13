from .models import Cart,CartItem
from .views import _cart_id


def counter(request):
    cart_count = 0
    if 'admin' in request.path:                                                                                         # cart not calculated in the admin interface
        return{}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))                                                       # get and filter by cart_id with session request
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:                                                                                # looping through the cart items, summing items quantity and adding them to
                cart_count +=  cart_item.quantity                                                                       #the cart_count
        except Cart.DoesNotExist:
            cart_count=0                                                                                                #if cart does not exist the cart count is set to
    return dict(cart_count=cart_count)