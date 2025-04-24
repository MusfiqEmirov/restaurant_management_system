from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from project_apps.accounts.models import User, Profile


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'created_at', 'is_deleted')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'created_at', 'is_deleted')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Soft delete', {'fields': ('is_deleted',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'phone_number', ),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', "address",'bonus_points', 'created_at', 'is_deleted')
    search_fields = ('user__username', 'user__email',)
    list_filter = ('is_deleted', 'created_at')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)