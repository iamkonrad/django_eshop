from django.db import models
from django.urls import reverse

from category.models import Category
from accounts.models import Account


class Product(models.Model):
    product_name= models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)                                                                    #by default always available

    #FK, connection with category model
    category = models.ForeignKey(Category, on_delete=models.CASCADE)                                                    #deleting a category removes products associated with it
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):                                                                                                  #accessing the slug of category and product, generating url
        return reverse('product_detail',args=[self.category.slug, self.slug])                                           #of a specific product

    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def colors (self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes (self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color','color'),
    ('size','size')
)

class Variation(models.Model):
    #FK
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=150,choices=variation_category_choice)
    variation_value = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

def __str__(self):
    return self.variation_value


class ReviewRating(models.Model):
    #FK
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)

    subject=models.CharField(max_length=100,blank=True)
    review=models.TextField(max_length=500,blank=True)
    rating=models.FloatField()                                                                                          #3.5,4.5 and so on
    ip=models.CharField(max_length=20,blank=True)
    status=models.BooleanField(default=True)                                                                            #setting to False will disable the reviews
    created_date=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


