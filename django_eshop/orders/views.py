from django.shortcuts import render, redirect

from carts.models import CartItem


def place_order(request):
    current_user = request.user                                                                                         #logged in user


    cart_items=CartItem.objects.filter(user=current_user)                                                               #if cart count less or equal to 0 redirect back to shop
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('store')

    if request.method=='POST':
        form=OrderForm(request.POST)
