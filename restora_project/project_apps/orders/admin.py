from django.contrib import admin

from project_apps.orders.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at', 'is_deleted')
    search_fields = ('user__email',)
    list_filter = ('status', 'created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('user', 'total_amount', 'status', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price', 'created_at', 'is_deleted')
    search_fields = ('menu_item__name',)
    list_filter = ('created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('order', 'menu_item', 'quantity', 'price', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)