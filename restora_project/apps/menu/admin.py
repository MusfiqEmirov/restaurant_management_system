from django.contrib import admin

from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') # cedvelde gorsenen sahe
    search_fields = ('name',) #axtaris ucun


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'discount_percentage')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
