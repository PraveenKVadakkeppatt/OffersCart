from django.contrib import admin
from .models import Product
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','product_slug','price','category','modified_date','created_date',)
    prepopulated_fields = {'product_slug':('product_name',)}


admin.site.register(Product,ProductAdmin)