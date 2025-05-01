import csv
from datetime import datetime
from django.contrib import admin
from django.http import HttpResponse

from project_apps.orders.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_type', 'created_at', 'is_deleted')
    search_fields = ('user__email',)
    list_filter = ('status', 'payment_type', 'created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('user', 'total_amount', 'status', 'payment_type', 'is_deleted')
    actions = ['export_sales_report']

    def export_sales_report(self, request, queryset):
        # Tarix aralığını queryset-dən alırıq
        orders = queryset.order_by('created_at')
        if orders.exists():
            start_date = orders.first().created_at.date()
            end_date = orders.last().created_at.date()
            filename = f"sales_report_{start_date}_to_{end_date}.csv"
        else:
            start_date = end_date = datetime.now().date()
            filename = f"sales_report_{start_date}.csv"

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Total Amount', 'Payment Type', 'Status', 'Created At'])
        for order in orders:
            writer.writerow([
                order.id,
                order.user.email,
                order.total_amount,
                order.payment_type,
                order.status,
                order.created_at
            ])
        return response
    export_sales_report.short_description = "Satış hesabatını ixrac et"

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