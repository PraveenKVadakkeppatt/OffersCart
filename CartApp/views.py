from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from CartApp.models import Cart, CartItem
from StoreApp.models import Product,Variations

# Create your views here.

# def cart(request):
#     return render(request,'cart.html')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            try:
                variation = Variations.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variations.DoesNotExist:
                pass

    # get or create cart
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # check if cart item exists
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    if cart_items.exists():
        ex_var_list = []
        id_list = []

        for item in cart_items:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)

        if product_variation in ex_var_list:
            # item with same variations exists → increase quantity
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            # new variation combination → create new item
            item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                item.variation.set(product_variation)
            item.save()
    else:
        # no cart item yet → create new one
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if len(product_variation) > 0:
            cart_item.variation.set(product_variation)
        cart_item.save()

    return redirect('cart')




def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id = product_id)
    cart = Cart.objects.get(cart_id = _cart_id(request))
    try:
        cart_item = CartItem.objects.get(product = product, cart = cart, id=cart_item_id)
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id = _cart_id(request))
    cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request,total=0,quantity=0,cart_items=None,tax=0,grand_total=0):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (.5 * total)/100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':grand_total,
    }
    return render(request, 'cart.html',context)


def checkout(request,total=0,quantity=0,cart_items=None,tax=0,grand_total=0):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            tax = (.5 * total)/100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':grand_total,
    }
    return render(request,'checkout.html',context)