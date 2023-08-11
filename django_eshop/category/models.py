from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=100, unique=True)                                                                #responsible for a unique url of the category
    descriptions = models.TextField(max_length=500, blank=True)                                                         #optional field
    category_image = models.ImageField (upload_to='photos/categories', blank=True)                                      #optional field

    class Meta:
        verbose_name ='category'
        verbose_name_plural = 'categories'                                                                              #instead of 'categorys'

    def __str__(self):                                                                                                  #string representation of a category_name
        return self.category_namem