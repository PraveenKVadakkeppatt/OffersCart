import admin_thumbnails
from django.contrib import admin
from .models import Product, ProductGallery, ReviewRating,Variations
# Register your models here.


@admin_thumbnails.thumbnail('product_images')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','product_slug','price','stock','category','modified_date','created_date',)
    prepopulated_fields = {'product_slug':('product_name',)}
    inlines = [ProductGalleryInline]

class VariationsAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active','created_date',)
    list_editable = ('is_active',)
    list_filter = ('product','variation_category','variation_value',)

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product','user','subject','rating','created_at')


admin.site.register(ReviewRating,ReviewRatingAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Variations,VariationsAdmin)
admin.site.register(ProductGallery)