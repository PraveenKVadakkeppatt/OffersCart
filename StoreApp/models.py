from django.db import models
from CategoryApp.models import Category
from django.urls import reverse

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    product_slug = models.CharField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/product')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)


    def get_url(self):
        return reverse ('product_details',args=[self.category.category_slug, self.product_slug])

    def __str__(self):
        return self.product_name
    


class VariationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def colors(self):
        return self.get_queryset().filter(variation_category='color', is_active=True)

    def sizes(self):
        return self.get_queryset().filter(variation_category='size', is_active=True)

    def storages(self):
        return self.get_queryset().filter(variation_category='storage', is_active=True)


variation_category_choice = (
    ('color','color'),
    ('size','size'),
    ('storage','storage'),
)
    

class Variations(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="variations")
    variation_category = models.CharField(max_length=100,choices=variation_category_choice,)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()

    def __str__(self):
        return self.variation_value