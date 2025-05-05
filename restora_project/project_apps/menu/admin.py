from django.contrib import admin

from project_apps.menu.models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_deleted')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('name', 'description', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percentage', 'is_available', 'created_at', 'is_deleted')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_available', 'created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('category', 'name', 'description', 'price', 'image', 'is_available', 'discount_percentage', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().saveGeomarketing(request, obj, form, change)