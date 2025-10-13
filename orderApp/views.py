import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from CartApp.models import CartItem
from StoreApp.models import Product
from orderApp.form import CouponApplyForm, OrderForm
from orderApp.models import Coupon, Order, OrderProduct, Payment

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Create and save payment
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()

    # Mark order as paid
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Apply coupon if present
    if 'coupon_id' in request.session:
        try:
            coupon = Coupon.objects.get(id=request.session['coupon_id'])
            if coupon.is_valid_for_user(request.user):
                coupon.used_by.add(request.user)
                coupon.used_count += 1
                coupon.save()
            del request.session['coupon_id']
        except Coupon.DoesNotExist:
            pass

    # Move cart items to order products
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send confirmation email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('order/order_recieved_mail.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Return response
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

    

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    tax = 0
    grand_total = 0
    discount = 0
    coupon = None

    # Calculate total and quantity
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (.5 * total) / 100
    grand_total = total + tax

    # Apply coupon
    if 'coupon_id' in request.session:
        try:
            coupon = Coupon.objects.get(id=request.session['coupon_id'])
            if coupon.is_valid_for_user(request.user):
                discount = (coupon.discount_percent / 100) * total
                grand_total -= discount
            else:
                del request.session['coupon_id']
        except Coupon.DoesNotExist:
            pass

    # Handle POST request
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.discount = discount  
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'discount': discount,
                'coupon': coupon,
            }
            return render(request, 'order/payments.html', context)
        else:
            return redirect('checkout')

        

def order_completed(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        

        subtotal = 0
        for i in ordered_products:
            subtotal = i.product_price * i.quantity


        payment = Payment.objects.get(payment_id=transID)
        discount = order.discount
        context = {
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'dicount':discount,
        }

        return render(request,'order/order_completed.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')



def apply_coupon(request):
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid_for_user(request.user):
                request.session['coupon_id'] = coupon.id
                messages.success(request, "Coupon applied successfully!")
            else:
                messages.error(request, "Coupon is invalid or already used.")
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon does not exist.")
    return redirect('checkout') 


def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request,'Coupon removed successfully.')
    else:
        messages.warning(request,'No coupon was applied')
    return redirect('checkout')
