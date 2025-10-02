from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from CartApp.models import CartItem
from CartApp.views import _cart_id
from StoreApp.form import ReviewRatingForm
from StoreApp.models import Product, ProductGallery, ReviewRating
from CategoryApp.models import Category
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

from orderApp.models import OrderProduct

# Create your views here.
def store(request,category_slug=None):
    categories = None,
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, category_slug = category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available = True)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products':paged_products,
        'product_count':product_count
    }
    return render (request,'Store/store.html',context)



def product_details(request,category_slug,product_slug):
    try:
        single_product = get_object_or_404(Product, category__category_slug=category_slug, product_slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id (request),product=single_product).exists()
        
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct=None

    reviews = ReviewRating.objects.filter(product_id = single_product.id, status=True)
    
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)

    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery,
    }
    return render(request,'Store/product_details.html',context)



from django.db.models import Q

def search(request):
    # products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()

    context = {
        'products': products,
        'product_count':product_count
    }
    return render(request, 'Store/store.html', context)


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form = ReviewRatingForm(request.POST,instance=reviews)     
            form.save()
            messages.success(request,'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                print(data)
    
                messages.success(request,'Thank you! Your review has been Submited')
            return redirect(url)