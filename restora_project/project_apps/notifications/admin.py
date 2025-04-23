from django.contrib import admin
from project_apps.notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_read', 'sent_at', 'created_at', 'is_deleted')
    search_fields = ('title', 'message', 'user__email')
    list_filter = ('is_read', 'created_at', 'is_deleted')
    ordering = ('-created_at',)
    fields = ('user', 'title', 'message', 'is_read', 'sent_at', 'is_deleted')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)