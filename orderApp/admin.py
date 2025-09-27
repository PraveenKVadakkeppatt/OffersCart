from django.contrib import admin

from orderApp.models import Order, OrderProduct, Payment

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','quantity','product_price','ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'order_number','full_name','phone_number','email','state','city','order_total','tax','status',]
    list_filter = ['status','is_ordered']
    search_fields = ['order_number','first_name','last_name','phone_number','email',]
    inlines = [OrderProductInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)