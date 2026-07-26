from django.contrib import admin
from .models import Category, Tag, Asset, Portfolio

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Asset)
admin.site.register(Portfolio)