from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse

from accounts.forms import RegistrationForm, UserForm,UserProfileForm
from accounts.models import Account, UserProfile, EmailNewsLetter
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
from urllib.parse import urlparse, parse_qs

from orders.models import Order, OrderProduct


def register(request):

    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name= form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username= email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,
                                               password=password)                                                       #from django MyAccManager model, passing all the above
            user.phone_number = phone_number                                                                            #can't be used in user directly bcz of model logic
            user.save()

            #USER PROFILE CREATION
            profile=UserProfile()
            profile.user_id=user.id
            profile.profile_picture='default/default-user.png'
            profile.save()


            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form=RegistrationForm()

    context = {
        'form':form,
    }
    return render(request,'accounts/register.html',context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                if CartItem.objects.filter(cart=cart).exists():
                    cart_items = CartItem.objects.filter(cart=cart)
                    product_variation = [list(item.variations.all()) for item in cart_items]

                    user_items = CartItem.objects.filter(user=user)
                    ex_var_list = [list(item.variations.all()) for item in user_items]
                    ids = [item.id for item in user_items]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item = CartItem.objects.get(id=ids[index])
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            for item in cart_items:
                                item.user = user
                                item.save()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, "You are now logged in.")

            referrer = request.META.get('HTTP_REFERER', '')
            parsed_url = urlparse(referrer)
            params = parse_qs(parsed_url.query)
            next_page = params.get('next', [reverse('dashboard')])[0]
            return redirect(next_page)

        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out.")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()                                                                    #decoding user's pk
        user = Account._default_manager.get(pk=uid)                                                                     #returning an user object
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.Is_active=True
        user.save()
        messages.success(request,'Congratulations. Your account has been activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid Activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders=Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context={
        'orders_count':orders_count,
        'userprofile': userprofile,

    }
    return render(request,'accounts/dashboard.html',context)


def forgot_password(request):
    if request.method =='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)

        # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = "Password reset"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'No such account exists!')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def resetpassword_validate(request, uidb64,token):
    uid = None
    try:
        uid = urlsafe_base64_decode(uidb64).decode()                                                                    #decoding user's pk
        user = Account._default_manager.get(pk=uid)                                                                     #returning an user object
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']= uid
        messages.success(request,'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'This link has expired.')
        return redirect('login')

def reset_password(request):
    if request.method =='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid=request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')

        else:
            messages.error(request,'Passwords do not match.')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request,'accounts/my-orders.html',context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile=get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES, instance=userprofile)                                #for passing profile picture file
        if user_form.is_valid()and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form= UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=userprofile)

    context= {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method =='POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request,'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'Passwords do not match.')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail= OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context={
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render (request,'accounts/order_detail.html',context)


def subscribe(request):
    if request.method =="POST" and request.POST.get('EmailNewsLetter'):
        email=request.POST.get('EmailNewsLetter')
        exists=EmailNewsLetter.objects.filter(email=email).exists()

        if not exists:
            EmailNewsLetter.objects.create(email=email)
            messages.success(request, 'Your email has been added to our database.')
        else:
            messages.info(request,'This email has already been added.')

        referrer = request.META.get('HTTP_REFERER', reverse('home'))
        return redirect(f'{referrer}#newsletter-section')


    return redirect(reverse('home'))
