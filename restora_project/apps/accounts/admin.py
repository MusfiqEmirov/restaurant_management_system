from django.contrib import admin

from .models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # admin panelde cedvelde gorunecek sahe
    list_display = ('username', 'email', 'role', 'is_active')
    # roleelre gore filter
    list_filter = ('role', 'is_active')

    # search_fields ilə istifadeci adina ve mailne gore axtris
    search_fields = ('username', 'email')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # ladmin panelde cedvelde gorunecek sahe
    list_display = ('user', 'address', 'loyalty_points')

    # search_fields ilə istifadeci adina gore axtris.
    search_fields = ('user__username',)


