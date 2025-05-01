from django.contrib import admin

from .models import Notification, DiscountCode, BonusPoints, AdminCode


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'is_read', 'sent_at', 'created_at', 'is_deleted')
    search_fields = ('title', 'message', 'user__email')
    list_filter = ('is_read', 'is_deleted', 'created_at')
    ordering = ('-created_at',)
    fields = ('user', 'title', 'message', 'is_read', 'sent_at', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Müştəri Email"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user_email', 'is_used', 'created_at', 'is_deleted')
    search_fields = ('code', 'user__email')
    list_filter = ('is_used', 'is_deleted', 'created_at')
    ordering = ('-created_at',)
    fields = ('user', 'code', 'is_used', 'notification', 'is_deleted')
    readonly_fields = ('code', 'created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Müştəri Email"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BonusPoints)
class BonusPointsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'points', 'last_notified_points', 'created_at', 'is_deleted')
    search_fields = ('user__email',)
    list_filter = ('is_deleted', 'created_at')
    ordering = ('-created_at',)
    fields = ('user', 'points', 'last_notified_points', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Müştəri Email"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AdminCode)
class AdminCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user_email', 'created_at', 'is_deleted')
    search_fields = ('code', 'user__email')
    list_filter = ('is_deleted', 'created_at')
    ordering = ('-created_at',)
    fields = ('user', 'code', 'notification', 'is_deleted')
    readonly_fields = ('code', 'created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Admin Email"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)