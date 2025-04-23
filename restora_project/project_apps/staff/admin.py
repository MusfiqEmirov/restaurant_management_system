from django.contrib import admin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'role', 'is_active', 'created_at', 'is_deleted']
    list_filter = ['role', 'is_active', 'is_deleted', 'created_at']
    search_fields = ['user__email', 'user__username']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('user', 'role', 'is_active')}),
        ('Soft delete', {'fields': ('is_deleted',)}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "E-poçt"

    def get_readonly_fields(self, request, obj=None):
        return ['created_at', 'updated_at']