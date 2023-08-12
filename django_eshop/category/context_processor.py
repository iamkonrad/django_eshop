from category.models import Category


def menu_links(request):
    links = Category.objects.all()                                                                                      #fetching all the categories
    return dict(links=links)                                                                                            #returning a dictionary with key links connected to category queryset