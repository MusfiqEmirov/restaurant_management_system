from django.contrib import admin

from project_apps.customers.models import BonusTransaction


@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'description', 'created_at', 'is_deleted')
    search_fields = ('user__email', 'description')
    list_filter = ('created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('user', 'points', 'description', 'order', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)