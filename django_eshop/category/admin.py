from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}                                                                   # automatically pre-populate the slug based on the value of
                                                                                                                        # category_name
    list_display=('category_name','slug')                                                                               # will get displayed in list view of Category

admin.site.register(Category, CategoryAdmin)                                                                            #registering category model using CategoryAdmin class to
                                                                                                                        #define its display