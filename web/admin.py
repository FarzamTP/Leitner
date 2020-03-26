from django.contrib import admin
from .models import Category, UserProfile, FlashCart

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(FlashCart)