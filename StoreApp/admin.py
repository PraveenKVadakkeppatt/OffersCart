from django.contrib import admin
from .models import Product,Variations
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','product_slug','price','category','modified_date','created_date',)
    prepopulated_fields = {'product_slug':('product_name',)}

class VariationsAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active','created_date',)
    list_editable = ('is_active',)
    list_filter = ('product','variation_category','variation_value',)


admin.site.register(Product,ProductAdmin)
admin.site.register(Variations,VariationsAdmin)