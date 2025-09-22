from django.db import models

from AccountsApp.models import Account
from StoreApp.models import Product,Variations

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=100,blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id



class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variations,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)


    def sub_total(self):
        return self.product.price * self.quantity


    
    def __unicode__(self):
        return self.product