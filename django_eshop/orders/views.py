from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from carts.models import CartItem
from store.models import Product
from orders.forms import OrderForm
from. forms import OrderForm
from .models import Order, OrderProduct, Payment
import datetime
from django.core.mail import EmailMessage



def payments(request):
    if request.method == 'POST':
        order_number = request.POST.get('orderID')                                                                      #fetching products by orderID

        if not order_number:
            return render(request, 'orders/payment_failure.html',)

        order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=order_number)
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.user = request.user
            order_product.product = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered = True
            order_product.save()

            order_product.variation.set(item.variations.all())                                                          #fetching all the variations


            product=Product.objects.get(id=item.product_id)                                                             #after payment reducing the stock of a product
            product.stock -=item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()                                                             #clearing the cart


        mail_subject = "Thank you for your order"                                                                       #sending an email once a transaction has been completed
        message = render_to_string('orders/order_received_email.html', {
            'user': request.user,
            'order':order,

        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()


        return redirect(reverse('order_complete', args=[order.order_number]))

    else:
        return render(request, 'orders/payment_failure.html')


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

            # CREATING A UNIQUE ORDER NUMBER
            yr=int(datetime.date.today().strftime('%Y'))
            day=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,day)
            current_date=d.strftime("%Y%m%d")
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
            return render (request, 'store')

    else:
        return redirect ('checkout')


def order_complete(request, order_number):
    order = get_object_or_404(Order, user=request.user, order_number=order_number)
    cart_items = OrderProduct.objects.filter(order=order)                                                               #fetching OrderProduct

    subtotal = sum([item.product_price for item in cart_items])
    grand_total = sum([item.product_price * item.quantity for item in cart_items])

    order.is_ordered = True
    order.save()

    context = {
        'order': order,
        'cart_items': cart_items,
        'order_number': order.order_number,
        'subtotal':subtotal,
        'grand_total': grand_total,
    }
    return render(request, 'orders/order_complete.html', context)
