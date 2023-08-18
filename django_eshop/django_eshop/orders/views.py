from django.shortcuts import render, redirect

from carts.models import CartItem
from orders.forms import OrderForm
from. forms import OrderForm
from .models import Order
import datetime


def payments(request):
    return render(request,'orders/payments.html')
def place_order(request, total=0,quantity=0):
    current_user = request.user                                                                                         #logged in user


    cart_items=CartItem.objects.filter(user=current_user)                                                               #if cart count less or equal to 0 redirect back to shop
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('store')

    grand_total=0
    tax=0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)                                                         # subtotal, product price by its quantity, adding to the total
        quantity += cart_item.quantity                                                                                  # adding the quantity of every cart item to the overall one
    tax = (16 * total) / 100
    grand_total = total + tax

    if request.method=='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user = current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_1=form.cleaned_data['address_1']
            data.address_2 = form.cleaned_data['address_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total= grand_total
            data.tax= tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

            #Order number
            yr=int(datetime.date.today().strftime('%Y'))
            day=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,day)
            current_date=d.strftime("%Y%mt%d")
            order_number=current_date + str(data.id)
            data.order_number=order_number
            data.save()

            order=Order.objects.get(user=current_user,is_ordered=False, order_number=order_number)
            context= {
                'order':order,
                'cart_items': cart_items,
                'total': total,
                'tax':tax,
                'grand_total':grand_total,
            }

            return render(request,'orders/payments.html',context)
    else:
        return redirect ('checkout')



