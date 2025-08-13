from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    category_slug = models.SlugField(max_length=50,unique=True)
    description = models.TextField(max_length=300, blank=True)
    category_image = models.ImageField(upload_to='photos/categories',blank=True)


    class Meta:
        verbose_name= 'Categorys'
        verbose_name_plural = 'categories'


    def get_url(self):
        return reverse('product_by_category',args=[self.category_slug])

    def __str__(self):
        return self.category_name
    