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
    