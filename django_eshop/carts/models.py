from django.db import models
from store.models import Product


class Cart(models.Model):
    cart_id = models.CharField(max_length=300,blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    #FK, many to- one
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product