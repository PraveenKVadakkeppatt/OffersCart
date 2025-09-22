from django.http import HttpResponse
from django.shortcuts import render,redirect
import requests


from AccountsApp.form import RegisterationForm
from CartApp.models import Cart, CartItem
from CartApp.views import _cart_id
from .models import Account
from django .contrib import messages,auth
from django .contrib.auth.decorators import login_required
# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('Account/accounts_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            # messages.success(request,'Registration Successful')

            return redirect('/account/login/?command=verification&email='+email)
    else:

        form = RegisterationForm()
    context = {
        'form':form,
    }
    return render(request,'Account/register.html',context)

def login(request):
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email,password=password)

        if user is not None:
            try:
                
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                    
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
               
                pass
            auth.login(request,user)
            messages.success(request,'You are successfuly logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                print('query->',query)
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect (nextPage)
                else:
                    return redirect('home')
            except:
                pass
                return redirect('home')
        else:
            messages.error(request,"Invalid Login Credentials")
            return redirect('login')
    return render(request,'Account/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are log out now')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulation! Your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid Activation Link')
    return redirect('register')

def forgotPassword(request):
    if request.method =='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)
            # Forgot Password
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('Account/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset mail has been sent to your email address ')
            return redirect('login')
        else:
            messages.error(request,'The Account is does not exit')
            return redirect('forgotPassword')
    return render(request,'Account/forgotPassword.html')


def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request ,'Please request your password' )
        return redirect('resetPassword')
    else:
        messages.success(request ,'The link is expired' )
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Password does not match')
            return redirect('resetPassword')
    else:
        return render(request,'Account/resetPassword.html')